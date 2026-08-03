# Draft for Eloise to send Nicholas (now optional/informational — the pipeline proceeds on operator approval, see APPROVAL.md; the fisher_kpp recipe question below was resolved by measured sweep: ic_modes=5, gap 0.041)

Hi Nicholas,

The round-2 audit found that three of the sharp datasets (phase_field_crystal_2d, fisher_kpp_2d, allen_cahn_2d) draw a random initial condition per sample without exporting it, so the field isn't a function of the condition vector. It's the same bug we fixed in June for the other nine variants, but the fix lived in a standalone script, so anything generated through the package path kept the old behavior.

I have two packages ready for your sign-off on branch `mffp-trunk-eloise` (nothing merged or regenerated yet):

- **IC-encoding fix** (`mffp_autoresearch/condition_completeness_proposal/`): the June fix moved into the package itself, all ten stochastic-IC modules now export their 16 IC coefficients, and generation fails hard if a dataset's condition vector doesn't determine its fields. Test suite is green (149 tests), and a small sample round at the production ladders certifies exact reconstruction from the condition vector alone. Figures in `sample_round/figures/`.
- **Ladder registration fix** (`mffp_autoresearch/ladder_fix_proposal/`): unchanged in content from when you last saw it, rebased so the patch applies at current HEAD.

One recipe decision before full regeneration: with the band-limited IC, fisher_kpp's LF-vs-HF gap drops from 0.196 to 0.024 (the 8-mode IC develops weaker fronts than white noise at T=0.05). Options:

- Longer output time, so the fronts sharpen and propagate.
- Smaller D range, for thinner fronts.
- More IC modes, at the cost of a larger condition vector.

allen_cahn keeps its gap (0.033 to 0.041) and pfc's missing gap predates this change.

Regeneration is solver time only, 500 samples x 3 levels per dataset. `SIGNOFF.md` in the proposal folder has the one-page summary and the exact commands. Could you take a look when you have a chance?

Thanks,

Eloise
