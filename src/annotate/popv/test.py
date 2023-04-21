import sys
import os
import pytest
import mudata as mu


input_file = f"{meta['resources_dir']}/pbmc_1k_protein_v3/pbmc_1k_protein_v3_filtered_feature_bc_matrix.h5mu"
reference_file = f"{meta['resources_dir']}/annotation_test_data/TS_Blood_filtered.h5ad"

def test_simple_execution(run_component):
    output_file = "output.h5mu"

    run_component([
        "--input", input_file,
        "--reference", reference_file,
        "--output", "output.h5mu",
        "--methods", "rf:svm"
    ])
    
    # check whether file exists
    assert os.path.exists(output_file), "Output file does not exist"
    
    # read output mudata
    output = mu.read_h5mu(output_file)

    # check output
    expected_rna_obs_cols = ["popv_prediction"]
    for col in expected_rna_obs_cols:
        assert col in output.mod["rna"].obs.columns, f"could not find columns .mod['rna'].obs['{col}']"

    print(f"output: {output}", flush=True)

if __name__ == '__main__':
    sys.exit(pytest.main([__file__, "--capture=no"], plugins=["viashpy"]))