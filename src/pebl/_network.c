#include "Python.h"

/* ****************************************************************************/
int
internal_is_acyclic(PyListObject *adjlist, PyListObject *tovisit, PyListObject *visited, int *checked) {
    register PyObject *node;
    register PyListObject *children;
    register int i,j,nodeid,cycle;

    int len_visited = PyList_GET_SIZE(visited);
    int len_tovisit = PyList_GET_SIZE(tovisit);
    
    // have we already visited a node in tovisit?, if so, cycle!
    for (i=0; i < len_tovisit; i++){
        for (j=0; j < len_visited; j++) {
            if (PyInt_AsSsize_t(PyList_GET_ITEM(tovisit, i)) == 
                PyInt_AsSsize_t(PyList_GET_ITEM(visited, j)))
                return 0; 
        }
    }
   
    // check each node in tovisit for cycles
    for (i=0; i < len_tovisit; i++) {
        // have we checked the node already?
        node = (PyObject *) PyList_GET_ITEM(tovisit, i);
        nodeid = PyInt_AsSsize_t(node);
        if (checked[nodeid]) {
            continue;
        }
        checked[nodeid] = 1;

        // children of node
        children = (PyListObject *) PyList_GET_ITEM(adjlist, nodeid); 

        // update visited list (add node)
        Py_INCREF(node);
        PyList_Append((PyObject *)visited, node);
        
        // check node for cycle
        cycle = !internal_is_acyclic(adjlist, children, visited, checked);
        PySequence_DelItem((PyObject *)visited, len_visited);
        Py_DECREF(node);
        if (cycle) 
            return 0;
    }

    return 1;
}

PyObject *
is_acyclic(PyObject *self, PyObject *args) {
    PyObject *adjlist, *tovisit, *visited;
    int *checked;
    int i, num_nodes, ret;

    if (!PyArg_ParseTuple(args, "OOO", &adjlist, &tovisit, &visited))
        return NULL;
    
    num_nodes = PyList_GET_SIZE((PyListObject *)adjlist);
    checked = PyMem_New(int, num_nodes);
    for (i=0; i < num_nodes; i++)
        checked[i] = 0;

    ret = internal_is_acyclic((PyListObject *) adjlist, (PyListObject *) tovisit, (PyListObject *)  visited, checked);
    PyMem_Del((void *) checked);

    if (ret)
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;

}

/* ****************************************************************************/

static PyMethodDef network_methods[] = {
    {"is_acyclic", (PyCFunction)is_acyclic, METH_VARARGS, "is_acyclic doc"},
    {NULL, NULL, 0, NULL} /* sentinel */
};


PyMODINIT_FUNC
init_network(void) {
    (void) Py_InitModule("_network", network_methods);
}

