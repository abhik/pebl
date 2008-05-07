#include <Python.h>
#include <bufferobject.h>
#include <numpy/arrayobject.h>


typedef struct {
    // Nijk and Nijk counts
    //   Nij = counts[j][0]
    //   Nijk = counts[j][k+1]
    //   so, Nij in the first column, Nijk in the rest
    int **counts;
    
    int *offsets;
    int num_parents, qi, ri, max_qi;
} CPT;

// cpt that can be reused. like a pool of size=1
static CPT *_oldcpt = NULL;


// get index into counts for given row of obs
int
cptindex(PyArrayObject *obs, int row, int *offsets, int num_parents) {
    register int i,ind=0;

    for (i=0; i<num_parents; i++) {
        ind += *((int*)PyArray_GETPTR2(obs, row, i+1)) * offsets[i];    
    }

    return ind;
}


// get index into counts for the given row
int
cptindex1(PyArrayObject *row, int *offsets, int num_parents) {
    register int i,ind=0;

    for (i=0; i<num_parents; i++) {
        ind += *((int*)PyArray_GETPTR1(row, i+1)) * offsets[i];    
    }

    return ind;
}

// construct and fill a CPT
CPT*
_buildcpt(PyArrayObject *obs, PyListObject *arities, int num_parents) {
    register int i,j;
    register int qi,ri;
    register int nx,ny;
    CPT *cpt;

    // child arity
    ri = PyInt_AsSsize_t(PyList_GET_ITEM(arities, 0));

    // parent configurations
    qi = 1;
    for (i=0; i < num_parents; i++) {
        qi *= PyInt_AsSsize_t(PyList_GET_ITEM(arities, i+1));
    }

    int len_offsets = (num_parents==0)?1:num_parents;

    // use existing cpt?
    if (_oldcpt != NULL) {
        cpt = _oldcpt;
        _oldcpt = NULL;

        // reallocate mem for new offsets and counts
        cpt->offsets = PyMem_Realloc(cpt->offsets, sizeof(int) * len_offsets);
        
        // qi > max_qi, so allocate more arrays
        if (qi > cpt->max_qi) {
            cpt->counts = PyMem_Realloc(cpt->counts, sizeof(int *) * qi);
            for (i=cpt->max_qi; i < qi; i++) {
                cpt->counts[i] = PyMem_Malloc(sizeof(int) * (ri+1));
            }
            cpt->max_qi = qi;
        }
        
        // reallocate and initialize arrays we need
        for (i=0; i < qi; i++) {
            cpt->counts[i] = PyMem_Realloc(cpt->counts[i], sizeof(int) * (ri+1));
            for (j=0; j < ri+1; j++) 
                cpt->counts[i][j] = 0;
        }
    } else {
        // create new cpt
        cpt = (CPT*) PyMem_Malloc(sizeof(CPT));
        cpt->max_qi = qi;
        cpt->offsets = PyMem_Malloc(sizeof(int) * len_offsets);
        cpt->counts = PyMem_Malloc(sizeof(int *) * qi);
        
        for (i=0; i<qi; i++) {
            cpt->counts[i] = PyMem_Malloc(sizeof(int) * (ri+1));
            for (j=0; j < ri+1; j++)
                cpt->counts[i][j] = 0;
        }
    }
  
    // update cpt
    cpt->ri = ri;
    cpt->qi = qi;
    cpt->num_parents = num_parents;

    // create offsets
    cpt->offsets[0] = 1;
    for (i=1; i<num_parents; i++)
        cpt->offsets[i] = cpt->offsets[i-1]*PyInt_AsSsize_t(PyList_GET_ITEM(arities, i));
    
    // adding to nij and nijk
    nx = PyArray_DIM(obs, 0);
    ny = PyArray_DIM(obs, 1);

    for (i=0; i<nx; i++) {
        j = cptindex(obs, i, cpt->offsets, num_parents);
        cpt->counts[j][0]++;
        cpt->counts[j][*(int*)PyArray_GETPTR2(obs,i,0) + 1]++;
    }

    // return the cpt
    return cpt;
}

// calculate the loglikelihood of data
double
_loglikelihood(CPT *cpt, PyArrayObject *lnfac) {
    register int j,k;
    double score = 0.0;

    // score is calculated as follows: 
    //    1) add log((ri-1)!) 
    //    2) subtract log((Nij + ri -1)!)
    //    3) add sum of log(Nijk!)
   
    score += cpt->qi * *((double*)PyArray_GETPTR1(lnfac, cpt->ri - 1));
    for (j=0; j<cpt->qi; j++) {
        score -= *((double*)PyArray_GETPTR1(lnfac, cpt->counts[j][0] + cpt->ri - 1));
        for (k=0; k<cpt->ri; k++) {
            score += *((double*)PyArray_GETPTR1(lnfac, cpt->counts[j][k+1]));
        }
    }
    
    return score;
}

// print CPT (useful for debugging)
void
print_cpt(CPT *cpt) {
    int j,k;

    printf("\n## CPT:\n");
    printf("ri=%d, qi=%d\n", cpt->ri, cpt->qi);
    for (j=0; j<cpt->qi; j++) {
        for (k=0; k<cpt->ri+1; k++) {
            printf("%d,", cpt->counts[j][k]);
        }
        printf("\n");
    }
}

// delete/deallocate the cpt
// if _oldcpt is null, we just set it to this cpt instead of freeing memory.
void 
_dealloc_cpt(CPT *cpt) {
    // _oldcpt doesn't exist, so set it to current cpt
    if (_oldcpt == NULL) {
        _oldcpt = cpt;
        return;
    }

    // _oldcpt exists, so just free this one
    register int j;
    for (j=0; j<cpt->max_qi; j++) {
        PyMem_Free(cpt->counts[j]);
    }
    PyMem_Free(cpt->counts);
    PyMem_Free(cpt->offsets);
    PyMem_Free(cpt);
}

/*****************************************************************************/

PyObject *
dealloc_cpt(PyObject *self, PyObject *args) {
    int pycpt;

    if (!PyArg_ParseTuple(args, "i", &pycpt)) {
        return NULL;
    }

    CPT *cpt = (CPT*) pycpt;
    Py_DECREF(pycpt);
    _dealloc_cpt(cpt);

    Py_RETURN_NONE;
}

PyObject *
replace_data(PyObject *self, PyObject *args) {
    int pycpt; 
    PyArrayObject *oldrow, *newrow;
    
    if (!PyArg_ParseTuple(args, "iO!O!", &pycpt, &PyArray_Type, &oldrow, &PyArray_Type, &newrow)) {
        return NULL;
    }
    
    CPT *cpt = (CPT*) pycpt;
    int old_index = cptindex1(oldrow, cpt->offsets, cpt->num_parents);   
    int new_index = cptindex1(newrow, cpt->offsets, cpt->num_parents);
    int oldval = *((int*)PyArray_GETPTR1(oldrow, 0));
    int newval = *((int*)PyArray_GETPTR1(newrow, 0));

    cpt->counts[old_index][0]--;
    cpt->counts[new_index][0]++;
    
    cpt->counts[old_index][oldval+1]--;
    cpt->counts[new_index][newval+1]++;

    Py_RETURN_NONE;
}


PyObject *
loglikelihood(PyObject *self, PyObject *args) {
    PyArrayObject *lnfac;
    int pycpt;
    double score;

    if (!PyArg_ParseTuple(args, "iO!", &pycpt, &PyArray_Type, &lnfac)) {
        return NULL;
    }
 
    CPT *cpt = (CPT*) pycpt;
    score = _loglikelihood(cpt, lnfac);

    PyObject *pyscore = Py_BuildValue("d", score);
    Py_INCREF(pyscore);
    return pyscore;
}
 
PyObject *
buildcpt(PyObject *self, PyObject *args) {
    PyArrayObject *obs;
    PyObject *arities;
    int num_parents;

    if (!PyArg_ParseTuple(args, "O!Oi", &PyArray_Type, &obs, &arities, &num_parents)) {
        return NULL;
    }
    
    // build the cpt
    CPT *cpt = _buildcpt(obs, (PyListObject *)arities, num_parents); 

    // return address of cpt as python int
    PyObject *pycpt = PyInt_FromSsize_t((int)cpt);
    Py_INCREF(pycpt);
    return pycpt;
    
}

static PyMethodDef cpd_methods[] = {
    {"buildcpt", (PyCFunction)buildcpt, METH_VARARGS},
    {"loglikelihood", (PyCFunction)loglikelihood, METH_VARARGS},
    {"replace_data", (PyCFunction)replace_data, METH_VARARGS},
    {"dealloc_cpt", (PyCFunction)dealloc_cpt, METH_VARARGS},
    {NULL, NULL} /* sentinel */
};


PyMODINIT_FUNC
init_cpd(void) {
    (void) Py_InitModule("_cpd", cpd_methods);
    import_array();
}

