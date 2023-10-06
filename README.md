# images-research

lab/
    data/
        images.json
        grype/
        syft/
        out/

    scan_images.py  - pulls, scans, and removes images
    build_ds.py     - builds the final csv from scan data
    scanner.py      - interfaces for grype and syft
    viz.py          - helpers for data visualization

    figures/
        image size by registry
        image n_comp by registry
        image n_vulns by registry
        
