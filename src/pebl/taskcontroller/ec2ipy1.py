import sys, os, time
import ConfigParser
from itertools import groupby

import ipython1.kernel.api as kernel
import boto

# options required in the config file
required_config_options = [
    ('access_key',          'Please specify your AWS access key ID.'),
    ('secret_access_key',   'Please specify your AWS secret access key.'),
    ('ami',                 'Please specify the AMI to use for the controller and engines.'),
    ('key_name',            'Please specify the key_name to use with the EC2 instances.'),
    ('credential',          'Please specify the ssh credential file.'),
]

class EC2Cluster:
    """
    * starts desired number of EC2 instances
    * starts controller on first instance
    * starts engines on all other instances

    * includes methods for:
        * creating and terminating cluster
        * creating RemoteController and TaskController from cluster

    states:
        * aws_connected: have connection to AWS
        * instances_reserved
        * instances_running
        * cluster_ready: instances are running and IPython1 controller/engines setup
    """

    def __init__(self, configfile, instances=[]):
        self.config = self._check_config(configfile)
        self.conn = boto.connect_ec2(
            self.config['access_key'],
            self.config['secret_access_key']
        )
        self._state = ['aws_connected']

        self.instances = instances if instances else []

    def _check_config(self, configfile):
        configp = ConfigParser.SafeConfigParser()
        configp.read(configfile)
        
        config = dict(configp.items('EC2'))
        for key, error in required_config_options:
            if key not in config:
                print error
                sys.exit(1)
        
        return config

    def _wait_till_instances_in_state(self, waitingfor, resulting_state, sleepfor=10):
        print "Waiting till all instances are %s. Will check every %s seconds." % (waitingfor, sleepfor)
        print "Hit Ctrl-C to stop waiting."

        while True:
            statuses = [i.update() for i in self.instances]
            if all(status == waitingfor for status in statuses):
                print "All instances %s" % waitingfor
                self._state.append(resulting_state)
                return
            else:
                print "Not all instances are %s" % waitingfor
                statuses.sort()
                for statustype, statuses in groupby(statuses, lambda x: x):
                    print "\t%s: %s instances" % (statustype, len(list(statuses))) 
            
            time.sleep(sleepfor)

    def wait_till_instances_running(self, sleepfor=10):
        self._wait_till_instances_in_state('running', 'instances_running', sleepfor)

    def wait_till_instances_terminated(self, sleepfor=10):
        self._wait_till_instances_in_state('terminated', 'instances_trminated', sleepfor)

    def create_instances(self, min_count=1, max_count=None):
        # if max not specified, it's the same as the min
        max_count = max_count or min_count
        
        # reserve instances
        print "Reserving EC2 instances."
        self.reservation = self.conn.run_instances(
            self.config['ami'],
            min_count, max_count,
            self.config['key_name'],
        )

        self._state.append('instances_reserved')
        self.instances = self.reservation.instances

        self.wait_till_instances_running()

    def start_ipython1(self, engine_on_controller=False):
        if not 'instances_running' in self._state:
            print "Not all instances are running."
            return False

        if not hasattr(self, 'instances'):
            print "Create EC2 instances before starting cluster."
            return False

        print "Starting ipython1 controller/engines on running instances"
        
        # redirect stdin, stdout and stderr on remote processes so ssh terminates.
        # we could use 'ssh -f' but that will fork ssh in the background
        # and on large clusters that could mean many ssh background procs
        cmd_postfix = "</dev/null >&0 2>&0 &"

        # run ipcontroller on the first controller instance
        controller_ip = self.instances[0].public_dns_name
        controller_port = kernel.defaultRemoteController[1]
        print "Starting controller on %s" % controller_ip
        self.remote(
            host = self.instances[0],
            cmd = "nohup /usr/local/bin/ipcontroller -l /mnt/ipcontroller_ %s" % cmd_postfix,
        )

        print "Waiting for controller to start (6 secs)"
        time.sleep(6)

        # run engine on the same instance as controller?
        engine_instances = self.instances[1:] if not engine_on_controller else self.instances

        # run ipengine on selected instances
        for inst in engine_instances:
            print "Starting engine on %s" % inst.public_dns_name
            self.remote(
                host = inst,
                cmd = "nohup /usr/local/bin/ipengine --controller-ip=%s -l /mnt/ipengine_ %s" % (controller_ip, cmd_postfix),
            )
            time.sleep(1) # so we don't bombard the controller..
        
        print "-"*70
        print "Ipython1 controller running on %s:%s" % (controller_ip, controller_port)
        print "Type the following to login to controller:"
        print "ssh -i %s root@%s" % (self.config['credential'], controller_ip)

        self._state.append('ipython1_running')
        return True

    def reboot_instances(self):
        print "Rebooting all instances"
        for inst in self.instances:
            inst.reboot()
        
        self._state = ['instances_reserved']
        self.wait_till_instances_running()

    def terminate_instances(self):
        for i in self.instances:
            i.stop()

        self.wait_till_instances_terminated()

    def authorize_access_to_controller(self, from_ip):
        ports = [kernel.defaultRemoteController[1], kernel.defaultTaskController[1]]

        for port in ports:
            print "Authorizing access for group default for port %s from IP %s" % (port, from_ip)
            self.conn.authorize_security_group('default', ip_protocol='tcp', from_port=port,
                                           to_port=port, cidr_ip=from_ip)

    @property
    def remote_controller(self):
        return kernel.RemoteController((
            self.instances[0].public_dns_name, 
            kernel.defaultRemoteController[1]
        ))

    @property
    def task_controller(self):
        return kernel.TaskController((
            self.instances[0].public_dns_name,
            kernel.defaultTaskController[1]
        ))

    @property
    def task_controller_url(self):
        return "%s:%s" % (self.instances[0].public_dns_name, 
                          kernel.defaultTaskController[1])

    @property
    def remote_controller_url(self):
        return "%s:%s" % (self.instances[0].public_dns_name, 
                          kernel.defaultRemoteController[1])


    # from Peter Skomoroch's ec2-mpi-config.py (see http://datawrangling.com)
    def remote(self, host, cmd='scp', src=None, dest=None, test=False):
        """ Run a command on remote machine (or copy files) using ssh.
            
            @param host: boto ec2 instance, ip address or dns name

        """
        d = {
            'cmd':cmd,
            'src':src,
            'dest':dest,
            'host':getattr(host, 'public_dns_name', str(host)),
            'switches': ''
        }

        d['switches'] += " -i %s " % self.config['credential']

        if cmd == 'scp':
            template = '%(cmd)s %(switches)s -o "StrictHostKeyChecking no" %(src)s root@%(host)s:%(dest)s' 
        else:
            template = 'ssh %(switches)s -o "StrictHostKeyChecking no" root@%(host)s "%(cmd)s" '

        cmdline = template % d  
        
        if test:
            print cmdline
        else:
            os.system(cmdline)

    def remote_all(self, cmd='scp', src=None, dest=None, test=False):
        for i in self.instances:
            self.remote(i.public_dns_name, cmd, src, dest, test)

    def tofile(self, filename):
        f = file(filename, 'w')
        f.writelines(inst.id + "\n" for inst in self.instances)
        f.close()

    def fromfile(self, filename):
        def _instance(id):
            inst = boto.ec2.instance.Instance(self.conn)
            inst.id = id
            inst.update()

            return inst

        self.instances = [_instance(id[:-1]) for id in file(filename).readlines()]

# USAGE
#ec2 = EC2Cluster()
#ec2.create_instances()
#ec2.start_ipython1()
#tc = ec2.task_controller
#ec2.terminate_instances()

