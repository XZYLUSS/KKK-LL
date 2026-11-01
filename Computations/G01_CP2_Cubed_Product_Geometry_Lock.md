# KKK-LL G01 - Exact Product Geometry of \((\mathbb{CP}^{2})^{3}\)

**Canonical ID:** G01  
**Role:** direct prerequisite for P01B.2-CURV  
**Input convention:** frozen G00 single-factor Fubini-Study normalization  
**Status in this document:** COMPLETE / FROZEN FOR P01B.2 PREREQUISITE SCOPE

## 1. Single-factor data

For each factor \(X_A=\mathbb{CP}^{2}_{A}\), \(A\in\{c,L,R\}\), with radius
\(b_A>0\), the G00 convention is

\[
R_{a\bar b c\bar d}
=\frac{2}{b_A^2}
\left(g_{a\bar b}g_{c\bar d}+g_{a\bar d}g_{c\bar b}\right),
\qquad
\operatorname{Ric}=\frac{6}{b_A^2}g_A.
\]

Consequently,

\[
R_A=\frac{24}{b_A^2},
\qquad
\operatorname{Vol}(X_A)=\frac{\pi^2b_A^4}{2},
\]

and, pointwise,

\[
|\operatorname{Riem}_A|^2=\frac{192}{b_A^4},
\qquad
|W_A|^2=\frac{96}{b_A^4},
\qquad
\mathcal L_2[X_A]=\frac{192}{b_A^4}.
\]

The integrated Lovelock densities are

\[
\boxed{
I_0^{(A)}=\frac{\pi^2b_A^4}{2},
\qquad
I_1^{(A)}=12\pi^2b_A^2,
\qquad
I_2^{(A)}=96\pi^2,
\qquad
I_{p\ge3}^{(A)}=0.
}
\]

The last equality is dimensional: a four-manifold has no nonzero Lovelock
density above order two.  The value of \(I_2\) also follows from
\(I_2=(4\pi)^2 2!\,\chi(\mathbb{CP}^{2})\).

## 2. Product curvature

For

\[
Y^{12}=X_c\times X_L\times X_R,
\qquad
g_Y=g_c\oplus g_L\oplus g_R,
\]

the Levi-Civita connection and Riemann tensor split block-diagonally:

\[
\nabla^Y=\nabla^c\oplus\nabla^L\oplus\nabla^R,
\qquad
\operatorname{Riem}_Y
=\operatorname{Riem}_c\oplus\operatorname{Riem}_L
\oplus\operatorname{Riem}_R,
\]

with all mixed curvature components zero.  Hence

\[
\operatorname{Ric}_Y
=\bigoplus_A\frac{6}{b_A^2}g_A,
\qquad
R_Y=24\sum_A\frac1{b_A^2},
\qquad
\operatorname{Vol}(Y)=\frac{\pi^6}{8}b_c^4b_L^4b_R^4.
\]

The product is Einstein if and only if

\[
b_c=b_L=b_R.
\]

Thus unequal radii are genuine shape moduli rather than a coordinate artifact.

## 3. Exact product Lovelock formula

The canonical Lovelock double-form product rule gives

\[
\boxed{
C_s(b_c,b_L,b_R)
=\int_Y\mathcal L_s[g_Y]\,\mathrm{vol}_Y
=\sum_{p+q+r=s}\frac{s!}{p!q!r!}
I_p^{(c)}I_q^{(L)}I_r^{(R)}.
}
\]

Only \(p,q,r\in\{0,1,2\}\) contribute, so \(C_s=0\) for \(s>6\).
Writing \(x_A=b_A^2\), the complete unequal-radius panel is

\[
\frac{C_0}{\pi^6}=\frac18x_c^2x_L^2x_R^2,
\]

\[
\frac{C_1}{\pi^6}
=3\left(x_cx_L^2x_R^2+x_c^2x_Lx_R^2+x_c^2x_L^2x_R\right),
\]

\[
\begin{aligned}
\frac{C_2}{\pi^6}={}&24\left(x_c^2x_L^2+x_c^2x_R^2+x_L^2x_R^2\right)\\
&+144\left(x_c^2x_Lx_R+x_cx_L^2x_R+x_cx_Lx_R^2\right),
\end{aligned}
\]

\[
\begin{aligned}
\frac{C_3}{\pi^6}={}&1728\left(
x_c^2x_L+x_c^2x_R+x_L^2x_c+x_L^2x_R+x_R^2x_c+x_R^2x_L
\right)\\
&+10368x_cx_Lx_R,
\end{aligned}
\]

\[
\frac{C_4}{\pi^6}
=27648(x_c^2+x_L^2+x_R^2)
+165888(x_cx_L+x_cx_R+x_Lx_R),
\]

\[
\frac{C_5}{\pi^6}=3317760(x_c+x_L+x_R),
\qquad
\frac{C_6}{\pi^6}=79626240.
\]

Each expression is exactly \(\mathfrak S_3\)-invariant.

## 4. Equal-radius regression

For \(b_c=b_L=b_R=b\), the panel reduces to the frozen C00 values:

\[
\boxed{
\begin{array}{c|c}
s&C_s(b)\\ \hline
0&\pi^6b^{12}/8\\
1&9\pi^6b^{10}\\
2&504\pi^6b^8\\
3&20736\pi^6b^6\\
4&580608\pi^6b^4\\
5&9953280\pi^6b^2\\
6&79626240\pi^6
\end{array}}
\]

At top order,

\[
C_6=(4\pi)^6 6!\,\chi(Y)
=(4\pi)^6 6!\cdot27
=79626240\pi^6,
\]

which is an independent Chern-Gauss-Bonnet check.

## 5. Pointwise generating data for P01B.2-CURV

Because every factor is homogeneous, define the pointwise Lovelock data

\[
(\ell_0^{(A)},\ell_1^{(A)},\ell_2^{(A)})
=\left(1,\frac{24}{b_A^2},\frac{192}{b_A^4}\right)
\]

and distinguish them from the exponential generating polynomial

\[
P_A(z)=\sum_{p=0}^{2}\frac{\ell_p^{(A)}}{p!}z^p
=1+\frac{24}{b_A^2}z+\frac{96}{b_A^4}z^2.
\]

The pointwise product Lovelock densities then obey

\[
\sum_{s=0}^{6}\frac{\mathcal L_s[Y]}{s!}z^s
=\prod_{A=c,L,R}P_A(z),
\]

where the coefficient convention includes the ordinary multinomial factor:
equivalently,

\[
\mathcal L_s[Y]
=\sum_{p+q+r=s}\frac{s!}{p!q!r!}
\ell_p^{(c)}\ell_q^{(L)}\ell_r^{(R)},
\quad
(\ell_0,\ell_1,\ell_2)
=\left(1,\frac{24}{b^2},\frac{192}{b^4}\right).
\]

Thus the factor \(96\) belongs to \(P_A\) because it is
\(\ell_2^{(A)}/2!\); it is not a change of the Lovelock normalization.

## 6. Scope boundary

G01 certifies the product tensors, topology, radii, and Lovelock invariants of
the prescribed geometry.  It does not establish that pure Lovelock dynamics
selects this topology, this product conformal class, equal radii, a stable
vacuum, a four-dimensional Planck sign, a gauge kinetic sign, chirality, or a
consistent finite Kaluza-Klein truncation.  Those are downstream gates.

## 7. Symbolic verification contract

The companion exact Python engine verifies, without floating-point arithmetic:

1. the real orthonormal Fubini-Study curvature tensor has
   \(\operatorname{Ric}=6g/b^2\), \(R=24/b^2\), and
   \(\mathcal L_2=192/b^4\);
2. the double-form wedge calculation on the twelve-dimensional product agrees
   with the multinomial formula at every order \(s=0,\ldots,6\);
3. the unequal-radius panel is permutation invariant;
4. the equal-radius panel reproduces C00;
5. the order-six coefficient reproduces \(\chi(Y)=27\);
6. orders \(s>6\) vanish dimensionally.
