# P01B.2-CURV - Stage A: Exact Curved Homogeneous Reduction

**Status:** calculation in progress; this stage derives and cross-locks the exact
equations but does not yet certify a healthy branch.  
**Prerequisites used:** P01A-G6.1.1, TOP00, G00, G01.

## 1. Four-scale geometry

For

\[
ds_{16}^{2}=-N^{2}dt^{2}+a^{2}d\Sigma_{3,\kappa}^{2}
+\sum_{A=c,L,R}b_A^{2}ds_{\mathbb{CP}^{2}_{A},\mathrm{FS},1}^{2},
\]

define

\[
H=N^{-1}\dot a/a,
\qquad
h_A=N^{-1}\dot b_A/b_A,
\qquad
\Psi_I=-\left(N^{-1}\dot H_I+H_I^2\right).
\]

The spatial second fundamental form is block diagonal with multiplicities

\[
(d_0,d_c,d_L,d_R)=(3,4,4,4).
\]

The Gauss curvature double form is

\[
\boxed{
\Omega={}^{(15)}\!R+K\mathbin{\wedge\!\wedge}K,
}
\]

with external intrinsic sectional curvature \(\kappa/a^2\), Fubini-Study
curvatures \(b_A^{-2}\mathcal R_{\mathrm{FS},A}\), and cross-block entries
\(\Omega^{ij}{}_{ij}=H_IH_J\).

## 2. Exact double-form normalization

Let \(\Omega^{\wedge k}\) be the \((2k,2k)\) double-form exterior power, and
let \(\operatorname{tr}_{\Delta}\) denote the sum of equal upper/lower mask
components.  The canonical Lovelock density on the slice is

\[
\mathcal L_k[\Omega]
=2^k\operatorname{tr}_{\Delta}(\Omega^{\wedge k}).
\]

This normalization reproduces

\[
\mathcal L_k(K\,\delta^{ij}_{kl})
=\frac{d!}{(d-2k)!}K^k
\]

in dimension \(d\), and reproduces the frozen G00 values
\(\mathcal L_1[\mathbb{CP}^{2}]=24/b^2\),
\(\mathcal L_2[\mathbb{CP}^{2}]=192/b^4\).

## 3. Lapse constraint

The exact lapse equation is

\[
\boxed{
\mathscr H
=\frac12\sum_{k=0}^{7}\alpha_k\mathcal L_k[\Omega]
=0,
\qquad \mathcal L_0=1.
}
\]

This equation contains arbitrary \(\alpha_0,\ldots,\alpha_7\), no normal
acceleration, and no local \(\alpha_8\) term.

## 4. Four evolution equations

For a representative spatial index \(i_I\) in block \(I\), the exact equation is

\[
\boxed{
\mathscr S_I
=\sum_{k=0}^{7}\alpha_k
\left[
\mathscr Q^{(k)i_I}{}_{i_I}
+\sum_{J=0,c,L,R}\mathcal M_{IJ}^{(k)}\Psi_J
\right]=0,
}
\]

where

\[
\mathscr Q^{(k)i}{}_{j}
=-\frac1{2^{k+1}}
\delta^{i a_1b_1\cdots a_kb_k}_{j c_1d_1\cdots c_kd_k}
\prod_{r=1}^{k}\Omega^{c_rd_r}{}_{a_rb_r},
\]

\[
\mathcal A_{(k)}^{ia}{}_{jb}
=\frac{k}{2^{k-1}}
\delta^{i a a_2b_2\cdots a_kb_k}_{j b c_2d_2\cdots c_kd_k}
\prod_{r=2}^{k}\Omega^{c_rd_r}{}_{a_rb_r},
\]

and the four-scale acceleration block is

\[
\boxed{
\mathcal M^{(k)}_{IJ}
=\sum_{a\in\text{block }J}
\mathcal A_{(k)}^{i_Ia}{}_{i_Ia}.
}
\]

These coefficient-extraction formulas are the explicit exact equations: the
companion engine expands them with integer/rational arithmetic for any symbolic
order or exact rational witness.  They retain the full Fubini-Study Riemann
tensor, not a constant-sectional-curvature replacement for \(\mathbb{CP}^{2}\).

## 5. Complete homogeneous acceleration map

The physical regularity test is not \(\det\mathcal M\ne0\) alone.  The inherited
G6 map is

\[
\boxed{
\mathcal A
=\sum_{k=1}^{7}\alpha_k\mathcal A_{(k)}:
\operatorname{Sym}^{2}(T^{*}\Sigma^{15})
\longrightarrow
\operatorname{Sym}^{2}(T^{*}\Sigma^{15}),
\qquad \dim=120.
}
\]

The exact engine constructs every component
\(\mathcal A^{ia}{}_{jb}\) and its \(120\times120\) component-basis matrix.
P01B.2 may pass only if this complete map, after the appropriate gauge/constraint
interpretation, has no forbidden characteristic direction on the candidate
branch.

## 6. Fixed-point coefficient system

At a static-radius de Sitter product,

\[
H=H_\star>0,
\qquad h_A=0,
\qquad x=H_\star^2,
\qquad y_A=b_{A\star}^{-2},
\]

the four equations are linear in \(\alpha_0,\ldots,\alpha_7\):

\[
\boxed{
\sum_{k=0}^{7}\alpha_k E_{I,k}(x,y_c,y_L,y_R)=0.
}
\]

Their exact coefficients are ordinary-multinomial products of

\[
\ell_{\mathrm{dS}_4}=(1,12x,24x^2),
\qquad
\ell_{\mathrm{dS}_3\perp}=(1,6x),
\]

\[
\ell_{\mathbb{CP}^{2}_A}=(1,24y_A,192y_A^2),
\qquad
\ell_{\mathbb{CP}^{2}_A\perp}=(1,12y_A).
\]

For the external equation, the factors are
\(\mathrm{dS}_3\times(\mathbb{CP}^{2})^3\); for the internal \(A\) equation,
they are \(\mathrm{dS}_4\times\mathbb{CP}^{2}_{A\perp}\times
\prod_{B\ne A}\mathbb{CP}^{2}_B\).  The common coefficient is \(-1/2\).

The double-form dynamic equations and these compact fixed-point products agree
order by order exactly in the companion regression.

## 7. P01B2A.1.2 frozen \(\rho=1\) controlled-slice audit

The numerical audit fixes

\[
H_\star^2=y_c=y_L=y_R=1,
\qquad y_A=b_{A\star}^{-2},
\]

and therefore fixes the independent dimensionless ratio

\[
\boxed{\rho=\frac{H_\star^2}{y}=1.}
\]

It is an equal-internal-radius, unit-curvature-ratio slice, not the complete
equal-radius branch.  In the four block-value basis the acceleration matrix
\(M\) is self-adjoint with respect to

\[
D=\operatorname{diag}(3,4,4,4),
\qquad DM=M^TD.
\]

The correct Euclidean symmetric representative and trace-sector spectrum are

\[
\boxed{B=D^{1/2}MD^{-1/2}=B^T,}
\qquad \operatorname{spec}(B_{\mathrm{Einstein}})=\{-1,-1,-1,14\}.
\]

P01B2A.1.2 uses \(\operatorname{eigvalsh}(B)\), never
\(\operatorname{eigvalsh}(M)\).  The first derivatives are constructed exactly
before the final numerical spectrum by

\[
\boxed{
\partial_v\!\left(\Omega^{\wedge k}\right)
=k\,\Omega^{\wedge(k-1)}\mathbin{\wedge\!\wedge}\partial_v\Omega.
}
\]

The calculation enforces a nonzero constraint-gradient norm, a maximum
four-scale condition number, and a maximum constraint-tangent leakage.  Its
necessary homogeneous kinetic-sign diagnostic is the Einstein acceleration
inertia \((1+,119-)\); a physical ghost verdict is deferred until the
constraint- and gauge-reduced tensor, radion, and vector residues are known.

The corrected deterministic sample contains

\[
4{,}000{,}000\ \text{coupling vectors},\qquad
249{,}706\ \text{nontrace-inertia feasible points},
\]

\[
249{,}573\ \text{points passing all enforced necessary conditions},
\qquad 0\ \text{stable points}.
\]

The invalid v1 trace operation omitted 27 legitimate trace-inertia passes; exact
constraint-tangent differentiation shows that all 27 are unstable.  The best
sampled growth exponent remains positive,

\[
\lambda_{\max}=0.644082166066\ldots>0.
\]

This is a finite-sample no-pass statement on \(\rho=1\), not a no-go theorem.

## 8. Explicit topological order

For the order-eight Euler density, define on each time boundary the second
fundamental-form one-form \(\mathcal K^a=-K^a{}_b e^b\), with the sign chosen to
match the frozen G6 positive-expansion convention.  The Euler transgression is

\[
\boxed{
Q_{15}
=16\int_0^1\!ds\,
\varepsilon_{a_1\cdots a_{15}}\,
\mathcal K^{a_1}\wedge
\prod_{r=1}^{7}
\left(
{}^{(15)}R^{a_{2r}a_{2r+1}}
-s^2\mathcal K^{a_{2r}}\wedge\mathcal K^{a_{2r+1}}
\right),
}
\]

and

\[
\boxed{
\mathcal L_8\,\mathrm{vol}_{16}=dQ_{15}.
}
\]

Thus

\[
S_8=\frac{\alpha_8}{2\kappa_{16}^{2}}
\left[
\int_{\Sigma_{t_2}}Q_{15}-\int_{\Sigma_{t_1}}Q_{15}
\right]
\]

up to spatial/asymptotic boundary pieces.  In the flat Bianchi-I limit,

\[
Q_{15}=16\,14!\,V e_{15}(H),
\qquad
\mathcal L_8
=\frac{16\,14!}{V}\frac{d}{d\tau}\left(Ve_{15}\right),
\]

reproducing the independent P01B.1 audit identity.  Therefore \(\alpha_8\)
is retained at action level but cannot alter the four bulk equations or the G6
acceleration matrix.  The companion exact engine now executes this identity and
the isotropic oracle \(16\,14!\,15H^{16}=16!H^{16}\) as mandatory regressions.

## 9. Stage-A verification and remaining gate

The exact engine checks:

1. all seven local orders against the flat P01B symmetric-polynomial equations;
2. all four fixed-point equations against independent product formulas;
3. construction of the complete \(120\times120\) map;
4. the Einstein limit
   \((\mathcal A\Psi)^i{}_j=\delta^i_j\operatorname{tr}\Psi-\Psi^i{}_j\).

Stage A does **not** yet authorize P01C-CURV.  The remaining P01B.2 work is a
general-ratio/equal-radius regression followed by an unequal-radius full-order
branch search, complete determinant margins, reduced physical residues, and
stability tests.  No branch will be called physically ghost-free from the four
fixed-point equations or homogeneous acceleration inertia alone.
