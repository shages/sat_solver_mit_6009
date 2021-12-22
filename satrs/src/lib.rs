use std::collections::{HashMap, HashSet};
use std::iter::FromIterator;

use pyo3::prelude::*;
use varisat::{CnfFormula, Lit, Var};
use varisat::{ExtendFormula, Solver};

/// Find a satisfying assignment
#[pyfunction]
fn sat<'a>(formula: Vec<Vec<(String, bool)>>) -> PyResult<Option<HashMap<String, bool>>> {
    // flatten literals
    let lits: Vec<(String, bool)> = formula.iter().flatten().cloned().collect();
    // get variable names, non-unique
    let vars: Vec<String> = lits.iter().map(|(v, _)| v.to_owned()).collect();
    // get unique variable names, and create index representation for each
    let var_set: HashSet<String> = HashSet::from_iter(vars.iter().cloned());
    let var_lookup: HashMap<String, usize> = var_set
        .iter()
        .enumerate()
        .map(|(i, v)| (v.to_owned(), i))
        .collect();
    let idx_lookup: HashMap<usize, String> =
        var_lookup.iter().map(|(v, i)| (*i, v.to_owned())).collect();

    // create varisat CNF formula from input
    let mut f = CnfFormula::new();
    for clause in formula {
        let mut c = vec![];
        for (vname, polarity) in clause {
            let var = Var::from_index(*var_lookup.get(&vname).unwrap());
            c.push(Lit::from_var(var, polarity));
        }
        f.add_clause(&c);
    }

    // solve and get answer
    let mut solver = Solver::new();
    solver.add_formula(&f);
    let sol = solver.solve().unwrap();
    if !sol {
        return Ok(None);
    }

    let mut result: HashMap<String, bool> = HashMap::new();
    for lit in solver.model().unwrap() {
        let idx = lit.index();
        let var = idx_lookup.get(&idx).unwrap();
        result.insert(var.to_owned(), lit.is_positive());
    }

    Ok(Some(result.into()))
}

/// A Python module implemented in Rust.
#[pymodule]
fn satrs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(sat, m)?)?;
    Ok(())
}
