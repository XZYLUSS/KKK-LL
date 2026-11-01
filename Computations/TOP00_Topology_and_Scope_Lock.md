# KKK-LL TOP00 - Cauchy-Topology and Branch-Scope Lock

**Canonical ID:** TOP00  
**Roadmap:** KKK-LL Harmonised Master Roadmap - P01B.1 No-Go Revision v3  
**Date:** 10 August 2026  
**Status in this document:** COMPLETE / FROZEN FOR DECLARED GOVERNANCE SCOPE  
**Direct prerequisites:** C00 and P01B.1-FLAT  
**Downstream handoffs:** P01B.2-CURV, P01B.3-GEN, P01B.M-FULL

## 1. Purpose

P01B.1-FLAT closes the following branch:

\[
\text{flat}+\text{diagonal}+\text{homogeneous}+\text{metric-only }D=16
+\text{persistent finite }3+12\text{ Hubble gap}
+\text{full G6 rank}.
\]

TOP00 prevents the revised programme from evading that result by silently changing
the differentiable manifold, importing \((\mathbb{CP}^{2})^{3}\) after the fact, or
confusing stabilization on a prescribed product with dynamical creation of a
product topology.

## 2. Global-hyperbolicity input

The classical branches governed by TOP00 assume a connected, smooth,
time-oriented, globally hyperbolic Lorentzian spacetime \((M^{16},g)\).  The
Bernal-Sanchez splitting theorem then gives a smooth spacelike Cauchy
hypersurface \(\Sigma^{15}\) and a global diffeomorphism

\[
M^{16}\cong I\times\Sigma^{15},
\qquad
g=-\beta(t,x)dt^{2}+g_t,
\]

for an interval \(I\subseteq\mathbb R\).  All Cauchy hypersurfaces in this
class are diffeomorphic.  Therefore smooth globally hyperbolic metric evolution
changes \(g_t\), not the diffeomorphism type of \(\Sigma^{15}\).

Consequently, a transition

\[
\mathbb R^{15}\ \longrightarrow\
\mathcal X^{3}\times(\mathbb{CP}^{2})^{3}
\]

is **not** part of P01B.2-CURV.  A topology-changing history would require a
separately declared singular, non-globally-hyperbolic, cobordism, boundary, or
quantum process and belongs to neither the present Cauchy problem nor the claims
authorized by this lock.

## 3. Fixed topology for the curved product branch

Every P01B.2-CURV run must choose, before initial data are specified, one member
of the following fixed-topology family:

\[
\boxed{
\Sigma^{15}_{\kappa,\Gamma}
=\mathcal X^{3}_{\kappa,\Gamma}\times Y^{12},
\qquad
Y^{12}=\mathbb{CP}^{2}_{c}\times\mathbb{CP}^{2}_{L}
\times\mathbb{CP}^{2}_{R}.
}
\]

Here \(\mathcal X^{3}_{\kappa,\Gamma}=\widetilde{\mathcal X}^{3}_{\kappa}/\Gamma\)
is a chosen complete orientable constant-sectional-curvature three-manifold,
with \(\kappa\in\{-1,0,+1\}\) after normalization.  The topology and quotient
group \(\Gamma\) are held fixed during a run.  Different choices of
\((\kappa,\Gamma)\) are different branches; no solution is interpreted as
evolving from one branch to another.

The three projective factors are already distinguished by the input labels
\(c,L,R\).  When their radii and couplings coincide the equations must retain
the permutation symmetry \(\mathfrak S_3\), but the labels are not claimed to
emerge dynamically.

## 4. Metric ansatz and dynamical content

P01B.2-CURV uses the multiply warped homogeneous product metric

\[
\boxed{
ds_{16}^{2}=-N(t)^{2}dt^{2}
+a(t)^{2}d\Sigma^{2}_{3,\kappa}
+\sum_{A\in\{c,L,R\}}b_A(t)^{2}ds^{2}_{\mathbb{CP}^{2}_{A},\mathrm{FS},\,b=1}.
}
\]

The lapse \(N\), external scale factor \(a\), and three internal radii
\(b_c,b_L,b_R>0\) are dynamical.  The Hubble/radion rates are

\[
H=N^{-1}\frac{\dot a}{a},
\qquad
h_A=N^{-1}\frac{\dot b_A}{b_A}.
\]

The ansatz fixes an orthogonal \(3+4+4+4\) product distribution at the outset.
It therefore tests:

1. existence of curvature-supported expanding/static-radius solutions;
2. stabilization and the relative selection of the three metric radii;
3. constraint propagation and full kinetic/principal-symbol health;
4. the basin of attraction, only after a P01B.2 pass.

It does **not** test:

1. creation of \((\mathbb{CP}^{2})^{3}\) topology;
2. discovery of a \(3+12\) split from fifteen unlabeled flat directions;
3. derivation of the labels \(c,L,R\);
4. emergence of the Fubini-Study conformal class from a generic metric.

Those stronger questions belong to P01B.3-GEN and its later P02-P04 gates.

## 5. Action and sector firewall

The P01B.2-CURV branch is metric-only maximal Lovelock gravity:

\[
S_{\mathrm{CURV}}[g]
=\frac{1}{2\kappa_{16}^{2}}
\int_{M^{16}}\!d^{16}x\sqrt{-g}
\sum_{k=0}^{8}\alpha_k\mathcal L_k.
\]

All local orders \(\alpha_0,\ldots,\alpha_7\) must be retained.  The order
\(k=8\) density is the sixteen-dimensional Euler density.  Its bulk Lovelock
tensor vanishes identically, but its reduced action must be exhibited as a
boundary/transgression term and retained in the action-level ledger.

No Yang-Mills field, fermion, \(G_6\) flux, abelian internal flux, or externally
prescribed stress tensor is permitted in P01B.2-CURV.  Turning on any such sector
defines P01B.M-FULL and changes the scientific claim.

## 6. Topological data fixed at entry

For each projective factor,

\[
\dim_{\mathbb R}\mathbb{CP}^{2}=4,
\quad
\pi_1(\mathbb{CP}^{2})=0,
\quad
H^{*}(\mathbb{CP}^{2};\mathbb Z)
=\mathbb Z[H]/(H^{3}),
\quad
\chi(\mathbb{CP}^{2})=3.
\]

Thus

\[
H^{*}(Y;\mathbb Z)
=\frac{\mathbb Z[H_c,H_L,H_R]}
{(H_c^{3},H_L^{3},H_R^{3})},
\qquad
\chi(Y)=27,
\qquad
\pi_1(Y)=0.
\]

The product is naturally Spin\({}^{c}\), while an ordinary spin structure is
not silently assumed.  These are immutable topological inputs.  Continuous
variables such as \(b_A\), volumes, curvature scales, and scale hierarchies are
metric data and remain dynamical.

## 7. Claim boundary by branch

| Branch | Fixed input | Dynamical question | Claim explicitly forbidden |
|---|---|---|---|
| P01B.2-CURV | product topology and homogeneous product conformal classes | four scale factors, stabilization, full-rank health | topology or unlabelled split emergence |
| P01B.3-GEN | compatible topology only | whether a generic metric develops a covariant \(3+12\) distribution | importing a product metric or labels |
| P01B.M-FULL | topology plus complete matter/flux sector conventions | coupled compactification of the full action | calling success pure Lovelock |
| P01B.D-DAE | flat characteristic endpoint | reduced constraints/gauge/strong-coupling classification | automatic reopening of P01C-FLAT |

## 8. P01B.2-CURV pass contract

P01B.2-CURV may authorize P01C-CURV only if it supplies all of the following:

1. the exact lapse constraint and four independent scale-factor equations with
   arbitrary \(\alpha_0,\ldots,\alpha_7\);
2. the explicit \(\alpha_8\) boundary identity;
3. at least one finite-radius fixed point with \(H_{\star}>0\) and
   \(h_{A\star}=0\);
4. the complete homogeneous tensor/radion acceleration matrix inherited from
   G6, not merely the four-dimensional minisuperspace block;
5. a nonzero branch determinant and quantitative distance from every
   characteristic surface;
6. positive four-dimensional graviton, physical radion, and relevant vector
   residues after constraint/gauge reduction;
7. a stability analysis with the same declared numerical tolerance throughout;
8. exact symbolic regression against Einstein, EGB, equal-radius, single-factor,
   flat-curvature, and topological limits.

Failure of any one item blocks P01C-CURV.  Fixed-point existence alone is not a
pass.

## 9. Governing disposition

\[
\boxed{
\mathrm{P01A\!-\!G6.1.1\ FROZEN}
\longrightarrow
\mathrm{P01B.1\!-\!FLAT\ COMPLETE/SCOPED\ NO\!-\!GO}
\not\longrightarrow
\mathrm{P01C\!-\!FLAT}.
}
\]

\[
\boxed{
\mathrm{TOP00}
\longrightarrow
\mathrm{G01}
\longrightarrow
\mathrm{P01B.2\!-\!CURV}
}
\]

TOP00 changes no Lovelock equation and rescues no flat solution.  It only fixes
the admissible manifold class and prevents overstatement of what the curved
product calculation can establish.

## 10. References

1. A. N. Bernal and M. Sanchez, *On smooth Cauchy hypersurfaces and Geroch's
   splitting theorem*, Commun. Math. Phys. **243** (2003) 461-470,
   arXiv:gr-qc/0306108.
2. A. N. Bernal and M. Sanchez, *Smoothness of time functions and the metric
   splitting of globally hyperbolic spacetimes*, Commun. Math. Phys. **257**
   (2005) 43-50, arXiv:gr-qc/0401112.
3. D. Lovelock, *The Einstein tensor and its generalizations*, J. Math. Phys.
   **12** (1971) 498-501.
4. R. C. Myers, *Higher-derivative gravity, surface terms and string theory*,
   Phys. Rev. D **36** (1987) 392.
5. D. Chirkov, A. Giacomini and A. Toporensky, *Dynamic compactification with
   stabilized extra dimensions in cubic Lovelock gravity*, Gen. Rel. Grav.
   **50** (2018) 98, arXiv:1804.02193.
6. K. Ohashi, *Ghost-Free Stable Minkowski Vacua in Lovelock Compactifications
   on Irreducible Symmetric Spaces*, arXiv:2601.09256 [hep-th].
