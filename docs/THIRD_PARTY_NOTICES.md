# Attribution and licensing

This is a review artifact. Packaging does not assign a new blanket license to the original project, imported data, or third-party components. Applicable upstream notices and dataset terms continue to apply. Before making a general public software release, the project owner should specify a license for the original contributions and confirm redistribution terms for imported assets.

- MFRNP: Rose-STL-Lab/MFRNP, source commit `614590a4ae7e0c9f2d0cc194640b0c41b7116a70`, MIT license. The upstream license is retained in `models/paper/mfrnp/upstream/LICENSE` and applies to the corresponding vendored copies. Repository: https://github.com/Rose-STL-Lab/MFRNP. Paper: Niu et al., ICML 2024.
- Multifidelity DeepONet: lu-group/multifidelity-deeponet, source commit `983e170773fe9a6b1f89f7e323154ac35fd844a5`, Apache License 2.0. Retained in `models/paper/mf_deeponet/upstream/LICENSE`, also applicable to corresponding vendored copies. Repository: https://github.com/lu-group/multifidelity-deeponet. Paper: Lu et al., Physical Review Research, 2022.
- The sharp-field solver package and extension verification references retain their bundled source notices. No separate license file was found for the local SURF solver source. It is not relabeled as MIT or Apache licensed.
- The extension verification material includes third-party reference projects. Their license/notice files are retained wherever supplied.
- ERA5 and the other imported data retain their original provenance. A code repository's software license is not asserted to license the underlying data. See the cited source publications and providers' applicable data terms.

Full scientific attribution and the distinction between inspiration, adaptation and vendored implementation appear in [model adaptations](MODELS.md) and [references.bib](references.bib). Third-party names and citations are intentionally preserved during account/path cleanup.
