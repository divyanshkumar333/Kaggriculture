"""
Agent V032: V031 + 4-Step Front-Running Lookahead
------------------------------------------------
Extends V030:
- Checks step + 1, then step + 2, then step + 3 for planned sales.
- If an item has planned sales at step + 3 and steps +1 and +2 have 0, pulls
  forward to step and records debt on step + 3.
- Tests whether a 3-step horizon captures further market margin or causes
  premature capital/inventory over-commitment.
"""

import base64
import copy
import json
import math
import zlib

_ACTIONS = json.loads(zlib.decompress(base64.b85decode(
    'c%0RpPp=(EZpFWfq4g{*%d$P$$<mux7}+xPXN-v<7zQ#yfMBw4vJ2+BN7B=~-Cg}7&mpU><XQRpUES^~7K=q59<qM^zkC1j>u-Pm+i&;&<+Gpf{rKqR%X@GB@Y%ip{Pn;8{eRy5>D~YQ{ny|A>u>-2?*D$i_wDPy{_^9C=TBZges%BdS3iAs^XT1&`(M8Ohd<x@?&*u0d&Z}CPkHpi)9)WWd-ssX&wqON2>9mZcQ-dbzWwm!<-3<RH&5Pu^Zm`U=Rdst@bL7_-H;yc-udPqfB5V;(Wj69{QAe^%eP7YeD9~5m#=Pzx_x^5=x+Giua5(~72hbbmp9Lz?FaV9a54|V$$XJb;j#$BBz}1Q;?;MzBi?<yTVr}cJdM-q@8nW>;kU1!K6~=Z+y8&{`XWl_U8mobX8G*V<D30j-S=O7`7LY7+pm9kwJqQ{hD~Aq^lmx**WUf}gGN4jb@L*5#ZEh&SKR&cK$4f4-D<}0hLfC?7*A$}->{qGywcDNcQ3$wJ)<fx$L$@tJd5f<Gkf{`_1%)76c?xmY5Q)5mshROj{O`!bXU@j&FF8hzn*ru@?4-Dwm6GwLettFfl?f2*ippGaCcgt{IRn(`{U!ZO7rU15ZrS0yG-Kd(X`U#^C1~7J-LMFrr&V<LFiS+%GzF^kNLyf;s5T28k=hM!{^VQ-8_Ev%b#vuyn6cV>A&4726#N;IppeEvO-mbL5as)4%GV4<IOTHyT(K=miY=x`Qh0OCG>vTmt@x{EPdn0AL?~~sF8}huzRO6M^NAlNdU0%wP)oQ_)R;P<2sLs!JA9~_dCeL=Hz*1iUQsUoxmrC!~e=#zcYw1ZICt(YW9@b`8A!Bf`{r3D?5B92ewJbIs-1Q-He1#%7K9TqdG;B_D-}0ybt!<W86u<FS#MCo0ujpZnQAgfCWs_wz3Q2@fBfqAe#k;M>7ssZ~%|6_x;m1FJHZQ^wYODFJAohJzoBMIa$jAA;B*F-Qx_|pMT+aA3v=>=L<)&b*^9ah+lQuUjUPxx;LC3&=fZ$9k7(?_ewV+KQXO&><n`xzeT|&;!W1GF$B&XkQK+Po)Y9LTEfGH=IjIp-qT8jo6?K%)!35+S?9?o53Jyfk-N0n`7ycGFh;wFjgV?*Y}<|*(dLftb3J6Y=(I?BfgK^|ySzkhm^)>s9NYA~^`AU-^5*!**~RQd;`R&sVV*t~s)7}yjk6h=dh!_GzgO8uFaA=?05YaQ%MqtGTd&ZEa#2S38hl(aNs1Qt1QK+Hd}plX-uqpyYY9|1%%Cc#-H#)<f%q;piREC##OBQ*itWIzFLEW^z-8_(eI5}nmQ@_mFLHC-$4*Cr<u_j6#R}1%jTFjM(uLH|+3@S^eSI;ikoM2o2n)MNUMQS~*_P|NDnQLVFm(>JoGXlj8*fS-Eb+XQ`AYtkwW@;FIw5INzk;N_VA|&Hc`_y+XLoRK$KUOzsU35Au6kNwTZFjHQm#tp%uHApM+vt_YCwOJ)CmI#nLT~m_>CBK?P0m+v|F~42%vyLI3SgET<7;x!LCn-C_M-*VD*p>f){?}$973(m-Y~|w6L}+J*I+QiS)rVf<z@7K`v)3Q@Rh-r_%9W^&JGBSmhMyWr!mFJ|BWSvI)ltvrO&um<=apn?mK^D~YDno?6wpqQ^x#VLkB4i|0SaDv>*qyAAmK`Mdw#mI>nNvDFE_JtUvNX+bk1K!*oHA@vvD;k5nZqKPPa**c)!9=Iu7@g-^SwR=7wm7~)#JW9<jkI%6Fud1u!RCcwcYQ?)8hY82)!+v^up5;DQ<x{*xeE+us3f;cp!JyB(2)dNsi?=<D{9Jo|I0Mer%tvq0m&by%C8k{`SwJoV*7#_yz$9G8Log!dHKZonJq+zxn}?KYAV^i%M2xVa`O*2)K@>^<pz1Ic*Wer}zbo`Q8fpkf8Cx)$yk(z6!a+xYDgEoLph$FLp0=V@^AvMRlS*2ELl`UiB(!3r>)_A@>OHmfkgLZEO^z&i{%eR{37%~FSRz!aXipw%h%~-&I!x|9vY(?%8){9!TQOsBw`LK&vtgA)Z;rk%qsGA5zV&N@`wB<2Dc6&y{~8UgF#?=v-nb)KirxA(#-h$4_5F%ByPu#}!lW+L$51T;Yr^(p2pNYx-SDxI2xw3Vb{yQO2NXa$^|)n}(IIj)LqHX5WkGN<>Y^g@yAP+rCR7t)r<_=;>^>ggM1_i3_&Gd#lNdN|)1|w)ew5;~%#Wi18oc3-A;-14sFhOLwziN9y}ds^;KYD@`U@TBCugkjHqwTD&N`4sxuVvkh@*oZ$M2oj$|Vln$nyqpH4noQbf$MN-_{0#eNVwe28bLt<_~n72J!O1Q`7dkUpNLPW7tS(2fB$|V(J1L2+mGIfzCyRFDtEJ<~t95(mX|t3>^b>_FA2N3OF?FUSsrH1k4tYlJYz&?bGF28keNmFKx7OyUP))2^K)uUMzF}^EWzBaXu}e$cwPDSGBI=qAv!cR0)eFi`8@A#fUa$a#}grL`4!4F-3)z!owg<xk6<>x-v#o;h!|hkOTY5^>=y56I3djoD`G_`Gw9`Yh^&fp@65DV_Kj|n?h^dnJ8n=dM#vcCtuPVMj@@F9HJ%UJbWMdp@Yh%8Zn(`L$p5+%2%Y-*xyBu#fX_bGlC%uD})iUCxYuJCg*?XkELc7cV_+jr_cWEx^H~SG0`!I09QnI<cb|$B7(rl`owxg<ZiEMQ@WrQ!u4c}k&N5%LhsOcEf*<9z8=%_jyBUBqwkyd58rsO?=|$}#51l8V!4cy+lIm6+E>j<(M2O)XVdLRQb=W~hEkM$$JCYhhbzid##Vp+%Z%|WX4#5bT?9M9$w5Ym8dYHetKu?k>Befe@DR=F5Uw&ia>EGjng}yV40(>SAc@BG$a|H#gsX*@W%%nRa<j#VcQXb8AYsLm@v;h%YN7L&bD=XUrs?nm*V5$oCRMToQw2!e<E*{suu7ICpjLR4keGDRSpPW0V~_yb!(T*2ovViIXQc@8Y!G(r^oT`I)7p@DjP1heK!FEbBEAp4)(4zDq`_=XtVN;OF23{PTD-r;Anc~e+VOYc7b+#3-+^SYR9$Y7KtZe=RD9|rFj@Sgv#w6<kwkDE!=?xX+xOc}LQqCc^So!iO83P1&d0;rUu9<qn6ADvlpo!a<b={kmQO0Na^lbgj8<40Q38nE0|OPA>>KgIgXu|7(nV*~0#0kLI0eZVC&z;F)7$x5c41KCHgkiBi!qBFy}?`M+-&`3!iowj#7P4U0P_@l5)bbyrLh7zNa$!{9&HH4KtMV^dJM*=U;C2IT-=4~B8;xGHW(yps-~AAt@EFFg4e-9(+Xu53?&CsAcU;O00-pIC(mRG2aHBsR0tlKKs6T)tPNE<9${)E0?;HW(p2U=1tzaWfQi(*5704)?UP}$GR<&g3tO&6iV+YKATC#UT2;zRsI@uw5|2x**KHO^QbFC(Ye`=Kh*ykS(RUoMB?tUP<11P;CFu^=N1~*8&uoc@a~>6-A#&pcphMeG<x$Eh6&lw*4!SFU6+XQZzRF}lZ#dHzHUJWX>0?mS6fE7Y?~p4Qcb7Wtv_4}=Ri4<WQ66*H?8%M=Q(1yMe}>^uwIN6|Y@LZV&W244l6-{ZE}r32dMThDZM(zQb%L}xsny@*QoF7srY@gsMogon|ECV`)nttDe(b6n7L8!mHt3jJiSD<5dvII6$iCcnRT^bL5P(QIp2QS12*yGXg`6wacd?ayr<BDcde054La|U4H!4QDDvrUzs1U^~OsjTWr*9>yg>dBmUw(Nw+r?mm&BHKp-cQEsD8(N;`>1$RQa}#R8JpFr653aJl`|GoxP1UdVOAOTQ|*vLIpTm~w&{2#MD?Iv`WW75?K1>LWJ8g@`l4iWNC6Ag6f<pw-bPyrL$`pA5o|;Oj(jLgfplf-&RE=cmU^(n;|l!P<uUr~P(Up~M>M};)yjrg=D~waC)j%1_roDpjG_7dV)rbI)}EX&k8#x*Zcxr77+}ICH_ER_389%9!sev{x$U9D;`jFy!KeuP@G=5*EV*MQRsz8%tKJ=rk#$;7V5jLlm7p60>VukznkU*zT<q;_bo);OAdK@_&IMS}VWODzw;H(@TVab%Yn6{5HThpC+KG$ru9F)rceY48I=|Dtn-`tP_vh?+vG79q3N%#SHM8=|6_a*5sipAw?cv?+>SZ?v7_o7lhA8A{eWB<1MYaY@DDVCDY`U36&OIq7j|v?YRHiUVu672YGPFfHc4r9mxV+S(KLAWMN~o@%04L0IQddwxaz5htx2p&#V2#kuty$7Fy*Yy9LhJgC`KBTJ$S*BQ-Ts)iV_a~_N~67n%rF?Wne+V{ot&`#+qLr9?)#fDpW>cV98Z4}B>Y>2w<?y$XMCjgg?W^(COUQFs~v8VgR!CwN1B_qd;@XAQu+e)<#m;=%!bUB&BvFpM{Z54o5Zy)2ctm?oU0U+VmSRr^Y&VuPnKB)`_j{4lGDB3(hyr_y&C_ZvGWdmR!VIj6<4u5s)2&oP9hzulHtoUwX|s*_9|v(=G|2r(++bk$2<^;u2{`c&2=$PG*8H2h^ngZ+tG;JlBS2hPCPs!^yEcTry`-LK=F4%S}(EVj}GiD+N;vu4XFQzjWc~*_rl<);s2V-12WBar&825vYso(BC@tg|N7~*gt(l7Tc)m8wg^q^#0j60VvgM!h;Tc-XiIGOGU}nPnDLnD8{*FUWuyg}`P~korrLef=$JmWWt1aS@!xFQ`d&|tO+vpJrl7I42~s!(6@5}T=CMKwxX|smuL0<jBz%|ayyNfNxPeLqhbTcO{+{A@a|kDC=+VEeol*}EYJX4~vLuy;_IVkXOk=O8DzhDdb^-6Se^=N{hF4%PKDDy+_ZO{x)Voq~Z7;6Z!mXAzXAd31nVf5dCY#rV9~Cxm@Zry5fP%y=sIIb&1u}li@RaCanP+TO^1P896+ksNH7i`U7_^6(&r)eZJ!xaq@~ym%dN(L37U&3Fyw;>d$)n*QwJj)-cky{?U!vGz6@h@sc6~ym-zu;MvG`a(FP=?1TVQ+(?u=AhqtrITZbWejN&1b%b{{u|v+46zM4r>q-PF+vY{1Qem$2*LxNQdGR+pdgS>mb(z6m`4w16Q}B}mr?dHfV#o?al6tVoil!Fs(vTM(g-QU4H$MLSAo#~+6FW@w2V2^|{d3iro=BkHy@Ju<JADmOFwIg{6eINB4M%2o1vS}A@p4V7eYXg(DhKrpj55#SL1gt<}SIQUVm@Hh`O4V0un&%@hls-JhCQGjFtj4J~tSyaGR*r5x$w4kVc3Ighi5p@-ykrhQKI?*FI49Xmc{<faF<uFFrv%JD(h;;U_{RG=&IuONd@J+TqB<P{~nee6(hH+}SB6FpyV<f(zDlJTHQ%U)BMFa;UNJqq{PNdyl>w&y-W&v+Q(hpK$@kuA<gvo$N#CY<RI3J4dR-pL=?m2)0YL3DdXod(wZK1u3Y3F3_j3QIqWT;_ARfR#-L6zm3L}zjnbXQ=d8-mdcL?q#CnuxtrqT~_PpX9)SRKz_MoMZ=+%m*&PAf}7KKa3|qiy`_J94y2ATX0~kvWKW$@G#PYipn+?@c4XE#}FKTQ7Tu@FY2|pL6uJnZoB<m7qoP4tvv#JAwB1s)h;W#E0pS9#2PPaqL2@-(#hcK3Db^k7IffM=6m*IT9T;Xg61>^F;vk=A@E-+x3?xKsc5~sSh}mNrT!4CJ|bf_;eCLUsJLijigA={p)bS&%_Wz|$j)~gEo>J|dP-uacrA@D+}JVEdcZYL1wx^h=%oxk4v}XcEqkphXNe3&=#lqqs5D8dY&U<Tx>cUw5ek3(nERr<21UB~dSjjO91A8}2{c?0>-|o9sw3elI!d2v8>b@1Dj&<BZi>c(`{;QFp)gp|Xqss?E6qml?4ns`VfYs=`YOcP&K04fDX7R4T@A8#7nkDRJ!61+Dpt}xm<sdgYvvj|?AN%FMDimGWq@$#EK<*Sj)f+lu%>1$e`jTZj2Elt1v2QxrM#LXk{0_b;O@_J21Phkri9on^Gf!9a+K?O>Y;3fb(d|j+ruZ*)(-t}YPxR4$#<a3HD9lsZ-^2#zEHS4k<6{!UlJ9w2t0v<%yGz#O{|z)!TA}Lb?BZCwXn>sm@QQ^>FN`7`Bg$1mS8QqBjBaXnTl;!p&Fx7GVIgOjBOlk8Y>lh+E0DcBxtL$FhdoGnVbi)%|#IhYBcvmPbZVGZ2J;!UT6{;tP+%EF|qn&GO@V%^$%Ww(rzjHYhc&PsoO&;Tt!JF7}F16b9^+(0Bs_4RJ-A07$tPY7Iy&D*nO*GwnHTA4^b@iQ&UZN9hjM*JF@Zx;db*7cV8M*0GxSF?btCM@>q=+E$&(+IRU|gN=mt+p)gs+ydAW0d=WAcs0B4|seP*NhEGhks8KB9iC&>~OP_a<_UfD|sS>s^tvCuxq=wC{xD#fdlpJ;0pPnW>rE=Ax8fSuZk*Y01LM5)YJ@9K3L+M@-qJN$~_R#6de<tQ-b4yA+D0y`*H_0o!MRuQ<jn;w+_NV}=RMnNYtl&8NA{lqtL`7i`*W^`GA&4A?MoCYJXyvZZ5mgdc@(wYwLIorw=7e?jItCr2TT0CHPF2NI=_V_83KecGdHPX;my(p3VGOSmINi|(ejCn9*(k#v(lk{O+wSAVC|svwFC$Y2Y5SFjs@5|vy_Bm5CGJ5_gZko<(h8qM_Q3*KX8IIOJI--qEZ04^@nFb}CM$2+w#!ssvujR77(U7zY>#pF6#ziJhQ}fcH!QdGsN|BV+A_^(n{g?1f_j36h+cmzwzjLHRw~E(g99!y9|G`Om~oQpB^(Odd?ajWVMrzyCUznu51O}pSdfJWN1xVbguG27kksxSzdp^VF%1DSiucybrN$~V&o<NTn-bAume%KQ_AbhyH*OtM<BAK7xlP=FHCLInrb*M6upYm|+lnM)C{aQ4w_@K_lF}Mz@;PMU>nim+2R2l%S9SfV06Qz7qQy?7I=Bknk%!T{{hA{jIzujnFys71=TfZ%*vR2){6M%RZja$`*>9db|KYu<FSq_IID|bqo9~=?<Oa8pk6uPQHRx=rZsPGN9F0ZGotc2WlqP{iH;pj#3?1@?l*@jOgNbM>dZghWcT9Z{Cu&UY2;Qjx#^;1Sh=|PrTZcJukcHomHm%yQv5FLW2YYhb2E6J3s~H!K1<}~eVsfZpWT^@rdsLfgyY}y*p`VxMrI|OPrbwX@I5X~4BF+>H<a6Wc)x10Gu5HmBEtS0gu)ONLsL*7^C<*bk%ytihL<9+@P^lH~$n(G?RWiojWpTGorStsOsd9lD9Q;$^#SKG^e95xLnyffVe2ODF;BQgtNoLG+Tzl3Lv5eS>K<&KB6%E3H2qO}zxwL?SyiZ@WGI^J+LP}u|#P6<+AM%cFWh&Az(SZORL%U`WB4owCB8mf<@V&govmVX`G2ygI^*Ht*-U^;@RED%1dJKE?xv-!7@j@xGJ62g=^wJ~b`wh$e7VTTdew;vJ714PXb@ft2m0H}#&wsiQCHZLmICs^ZE*%*@MH(`24P4JGnv}#87n3o^X|3waB)ue~eNdI2DU5%P&KN$RDqR-T29xA)zJ1~<EuDgy1@;`Z&dHO$XC;Y+QG6p3t5HB;_4kffGhqaZ`2<^D`fIg%RQb37En0!rRz@KLM?0ky8Q{CtoaG*ZGAtAm-u=r9_fAAF2{rG!+a6WHapWTZ*56$-sUSQ7bccwXQ%$_`NDCeFMG?}sub)19^2=Kv?A7a(8d#`+%qN8!TC`gjEWCZj<D1b@i?qT>-Q}?MWo;(PXzyOewktoGBR+rzt@GtEOBDF#sm|@t_hY-K;0Qhg`J+5Kr^(29K1CxDJS+<qOks+~0V*3w>0}t9SC>sQIArHCkz_?U;yp5x?v}~y*Bht|ES^Lp#BpQY`)cbT>^W+mSfOS_D!HwFp)B5D98M>9H7i%e1|p(BR~|mKo8W0s^e1_4<uxc9AW4&H51bmym8#1m;FvQ!^W68?Rdl~u4z`1KOb>T^aBGFGP-yJ3Pp?UOyzae{=>?C|Wzl8arg3Uk2zOScO$MelwyP+}6^sBqF3t!nrRfL|jI`gN1BwWKiVMhPSZxN80#!v?=CG;Y&ZN9*TJb|1goN?P8p2DSo{9U);6OC0bFr+c?aAF{A%z^J-Q8NtsV&IzE8Wh3-1XRjHWdT_wo2i0TqP&HFufip^g}F&k2uTxbT0PMZS0K8z4|u_Zv{xyuVoX;CmnwY9(cPRg=VT@soYhp`bj^c<Kkjm-TGsBzRKW{;Ei(0*$1m<G-s^kHzNFHW~??<EILy2+avtIytA>yNhQy$JZ$v@Sh4L<m|3~F7wZZe0tF=%9mwL~{WvcAca~$D>tdld8RG%uy`TQrQA4+%yBJm+GDimT4s;`=yV(eTj-#`ES^y!ey3wv*8u~%L5UDJO7#@y#QH2<S=YBP8$vl>@YAwVTS$1!p@FVlT`QQbx2HP2O#51xc7zz!lARs2Y=c8WGrx6eJZwWwAM%slD473=}L<NKJKRqYR!zl%j2@qFp0!jc`dG3G3u@+SNVt{>Sse*yFAoO4@1D1qDQ!BaE65-?HlolEVyb;qyOe@;EqsAXar%HiM#&XWW=TYi_HY@*7$y<?;El2T4KFOgEqS1(?uqp(>KZ2S#%UHi#J_aXB)gr1YuYhlw(L)8f54I7-+l8BBj^7tJIyOCxmX6QHi}VWYE>YnldZBi#jG6QgwG&Ni<w{i}Kj+pYibfmeJ}h1PK*ndHdxSFPh7B5ex|?~ZoQ|W)%y}a+@ra(E8=6VGTFpd=RFPd(sbak;Gn8&o1qts9)uW@v&_AuYZU+?TmOiuOSmtP9&^U|e7$Lk1n5$I~4qc$ox@??tKqy^qI!;A6PN$A0Eo19?Y}h}g#0{h=;`gV2DJF&xdEO-<rw`$%X!qt|qF^f=8J^Z%Y2%|lA&yFdiT~Ca_*6Ng1&Tfx4}@xkBe@|M!{_CGoi-A}V~fuT^~)+<s8fF!L>zYW;^<M=D?s$G6XoA0{)rlG8-s})dz~5Nh}UmDr%s|=w}mgKU55xjQAk9tM~-J7Y}^83Dyu#uUQ*!5!J(5EOpq5In;N4xrSfb$TUjeL#TtZh<)0k*d0Ym!GlJao=wpgDQNcN22A7dW-DQcP#T9MzxFed=6S)Gq@x09Fy^|Q>T`FpBiVWUr6`sw-<d3u~oR;Xl-CW>jW|+BCP#XjxX#rDbbAyTH_)?=@yZSP91+s)-5%Qb}k0~3FhmpN@e0d=QWbWSop7u0ddrT2>2!k6b9u3g2$vAaTjHWsEFSoY8>SG{S8dhEUXz3bOO6P#kvLb9<1F$1$Uk+>#G<6FiL0&fTw#M{H;n39~1L*`&=wLbXt(;S3kj)qOXNYEUgeb|`$nh<K1G#e$tv!T2BC4^b()Af;1Fl;Pg+I+Tr0+hN;B$v2cdD4n@Slhi_duOX<6+iCf^7axkM5>;<Hgb1tQbvXD-1XB^VN7)baD}FwZ4C^;E0KAvQXDbnUew~a|g7c{!)geB5k=0bX2Xr_!CYXQK^?YTgD7piNS}5v*l<DmjN4iPUDeXV3$Z#z(zZcS(~p}BDD-^g|$=Jt%_~P2v8y^q2#S<KH_iiQKa+XWwIN(jQPGaKq{9bW4XhLm9aG}K&91A6ZeSf^wBjrQh6~?<!)CWk`STg684h>{SA0qu1qrK-J?7cNY|XEDG<eIH5?`demCmX1nGly8G%yN68U>T>>~LO1vrzeI)&t-S$48NtiHYNzdvQ;s;R)v<-H7!izjd-x8gvi!Gt!>S~tNu6X%Vh#^y!qfui14R>aF&xcM{(dT`Sj5lxN?831T5jJTGB_)9@GYF>scz%K1X7nak!M#3HD%%_ofC-#=6Rh{tO+eZIa?JS>Hqh7y4bs@I4zRT6AC%Z7yHX;-#H=yN&M3i_{0$;1tPgH99%-Xd^_bh)oHg>rKX?@CeS_PiHI74d_G@a<{w&AkZlRela+%NPuMBF7km$}G5VUW2)DH#?Hn?m7@=OfE(4XegUfOa(Y9QMfR?=9BU`@yiQ`Dt2z0aXJxl~)lNF7Yk<(7h?KM2Fj<anjV-Y~2iU6njrViW0Z<TSaM<ePYCilQg)QP+o(r>@Qo42`EY}AswJ&M?S}>#flVdfg<Hl9V*q6Qbzo=s+~<=ZwHO@3)Gy<6)Y}O#o7r0<Nm`4->3AWDv~N$KQ_EMX3?#YQy_~b`JqWu@lZ9XLtaA;e(Opx!Nd+ZWo^Q%z`KnLf4Gzu7Y>Xe6+smT?xXi<!WtK6hckq=iIFKjCIigN*!QEQesh8cm$T6j<~sc`nolQq7LjCiXh*TQ(9cARwhzbYF_{gS|KCNw_YMGtbNaeEYF&RQ`uFTkElo?y{&7^6_+a>@7m`=14QVpHhU({!o{2GAVHcQh?To7EoT2Q!3`r%u2@i#6RJs$DH*WOmDtD4d&r}p!PHDB|qY#J_9r{xj*Z0w<ga>~7n{$()yK3u-c#Pg<Dq{1&z3mZV+@e-ZQco*{y)?oX<3yr@CX<qr!2-qIw?J#75Fko$R$%H0tb3haW4tAmHm@<wi<;jAC*}u;uwL{b>)2H#vm*BhY*SHN^x0$7tG91%65Ymy0^!&-?WsV949rU1#!!M<kc_e2&gQ~WmzDT|k$NOmG!#<g^eR^?$a3lnHp%f4)4F9DxET#vBb`<fEElZR!b>edF&j!H0)2}5^1-ruXQj*tP0p+OoTB3#A=@_sV`tMREgUZ?{cr@_Hxq$0xV-#}x*+B2<t0#Zk-MYIvlRB|fD1Hpo!%wb|0>?<9jIk#H~ba6qABl55fO~bfiv*re)^CVl@2->jv^H^UKYbE2|FKX4I2^EZ82=(4=P=dxJao^rbfLs`$I=Aq=se`r7U-38`3Tm>(uHZUBdDz4MB%T@dmQ*#lSGbr`sPH(S=)6*^!(J{is5+X7nANl6UR3!ZXs&vD!AaiIf!+;uw9apif!Aly%Uj708;deQ(pTU&(PeM$MeJ{}KCQIIdJ><aFHklF#zw4eHi~xkXtPP{h#JtTv2M+$!2|R^#6)!YI<p8NVY@guDrk*J{P;<hpmbi7coN0~)B^HRw`76&hH&k_zH7Q7EI*{6{(%#FK^Sx16e1;CN6X!+YVB_ZQlm3v=dE(gM(uBbC~k<tq87Jm?%hsZ9pha4ysCKq|vD&Q&$9hes4=Aqj&%wQnX6`HT2y80RlXR6)(f(Mh99nlq}k%^gmO1_-hC2NqSq3J<vAhsGyTc|*7r#3J?K^t;ZF?_(>yq`Cl{rV4{b$x*6{VnUqLC2*RnULA&?%)3ob$xHFLV>URZ#bO)5E$Enq%8pVD?tF*zY(peOl}3ywG{HD-fIR#*18)@|Mq{KF`^wr>)^R09D7LvMtn0Tmos%o>A)5+Ka<dj<W(OG{ua>L&UH*iIvhu#67b*xK7QYx4LORM1Qbi7wRxW4yh|FFXtt5;Ys2EpMzn@$*dez@w%>Wq;d9Pah$?4b8fVTsG?{Qs{a*)5qDdYp&fi3VYGU8745lUYMpE0Qix_h$<sPhziel^iPUus3v56U668%XEB7#GP>Z0<w|x}u68-u&au{{v2qh>Q')).decode("utf-8"))

_FR_ITEMS = ('MELON', 'MILK', 'STRAWBERRY', 'WOOL')
_FR_STATE = {
    0: {"last_step": -1, "due": {}, "spoiler_score": 0, "prev_inv": {}, "last_action": None},
    1: {"last_step": -1, "due": {}, "spoiler_score": 0, "prev_inv": {}, "last_action": None},
}
_WEED_STATE = {0: {}, 1: {}}
_WEED_REPLAY_STEPS = 8
_SHOP_PRODUCTS = {
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}

_MARKET_PARAMS = {
    "WHEAT": {"base": 25, "I0": 10000, "T": 400, "below_func": "sqrt", "below_target": 0.80, "above_func": "log", "above_target": 0.20},
    "CARROT": {"base": 35, "I0": 10000, "T": 450, "below_func": "hinge", "below_target": 1.00, "above_func": "sqrt", "above_target": 0.70},
    "TOMATO": {"base": 60, "I0": 10000, "T": 200, "below_func": "hinge", "below_target": 0.40, "above_func": "sqrt", "above_target": 0.60},
    "STRAWBERRY": {"base": 120, "I0": 10000, "T": 100, "below_func": "sqrt", "below_target": 0.70, "above_func": "linear", "above_target": 1.60},
    "MELON": {"base": 250, "I0": 10000, "T": 300, "below_func": "log", "below_target": 0.20, "above_func": "sq", "above_target": 3.60},
    "EGG": {"base": 50, "I0": 10000, "T": 332, "below_func": "hinge", "below_target": 0.40, "above_func": "log", "above_target": 0.20},
    "MILK": {"base": 160, "I0": 10000, "T": 122, "below_func": "sqrt", "below_target": 0.60, "above_func": "linear", "above_target": 1.60},
    "WOOL": {"base": 200, "I0": 10000, "T": 105, "below_func": "log", "below_target": 0.20, "above_func": "sq", "above_target": 3.20},
    "FERTILIZER": {"base": 100, "I0": 10000, "T": 200, "below_func": "linear", "below_target": 0.40, "above_func": "linear", "above_target": 0.40},
}

def _shape(func, x, T=None):
    x = max(0.0, float(x))
    if func == "linear": return x
    if func == "sq":     return x * x
    if func == "sqrt":   return math.sqrt(x)
    if func == "log":    return math.log(1.0 + x)
    if func == "hinge":
        if not T or T <= 0: return x
        u = x / T
        return u + 8.0 * max(0.0, u - 1.0) ** 2
    return x

def _market_price(item, inventory):
    p = _MARKET_PARAMS.get(item)
    if not p: return 1
    base, I0, T = p["base"], p["I0"], p["T"]
    if inventory < I0:
        f = p["below_func"]
        amp = p["below_target"] * base / _shape(f, T, T)
        price = base + amp * _shape(f, I0 - inventory, T)
    else:
        f = p["above_func"]
        amp = p["above_target"] * base / _shape(f, T, T)
        price = base - amp * _shape(f, inventory - I0, T)
    return max(1, int(round(price)))

def _get(value, key, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    getter = getattr(value, "get", None)
    if callable(getter):
        return getter(key, default)
    return getattr(value, key, default)

def _copy_action(action):
    action = copy.deepcopy(action or {})
    return {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands": [list(order or ["PASS"]) for order in (action.get("hands") or [])],
        "market": [list(order) for order in (action.get("market") or [])],
    }

def _seat(obs):
    return 1 if int(_get(obs, "player", 0) or 0) == 1 else 0

def _farm(obs, seat):
    farms = list(_get(obs, "farms", []) or [])
    return farms[seat] if seat < len(farms) else {}

def _align_hands(action, obs):
    action = _copy_action(action)
    expected = len(_get(_farm(obs, _seat(obs)), "hands", []) or [])
    hands = list(action.get("hands") or [])
    if len(hands) < expected:
        hands.extend([["PASS"] for _ in range(expected - len(hands))])
    action["hands"] = [list(order or ["PASS"]) for order in hands[:expected]]
    return action

def _tile_at(farm, position):
    try:
        x, y = int(position[0]), int(position[1])
        return (_get(farm, "tiles", []) or [])[y][x]
    except (IndexError, TypeError, ValueError):
        return "LOCKED"

def _trace_actor_action(step, actor):
    trace = _ACTIONS[min(max(int(step), 0), len(_ACTIONS) - 1)] or {}
    if actor == "farmer":
        return list(trace.get("farmer") or ["PASS"])
    hands = trace.get("hands", []) or []
    return list(hands[actor] if actor < len(hands) else ["PASS"])

def _weed_repair_action(obs, action, step):
    action = _align_hands(action, obs)
    seat = _seat(obs)
    game = _WEED_STATE[seat]
    if step == 0 or step < int(game.get("last_step", -1)):
        game = {"last_step": step, "active": {}}
        _WEED_STATE[seat] = game
    game["last_step"] = step
    farm = _farm(obs, seat)
    positions = [_get(farm, "farmer"), *list(_get(farm, "hands", []) or [])]
    unit_actions = [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]
    active = game.setdefault("active", {})

    for actor, transaction in list(active.items()):
        index = 0 if actor == "farmer" else int(actor) + 1
        if index >= len(unit_actions):
            active.pop(actor, None)
            continue
        age = step - int(transaction["start"])
        if age == 1:
            unit_actions[index] = list(transaction["intended"])
        elif 2 <= age <= 1 + _WEED_REPLAY_STEPS:
            unit_actions[index] = _trace_actor_action(step - 1, actor)
        else:
            active.pop(actor, None)

    for index, (position, intended) in enumerate(zip(positions, unit_actions)):
        actor = "farmer" if index == 0 else index - 1
        if actor in active or not isinstance(intended, list) or not intended:
            continue
        if intended[0] not in ("BUILD_PASTURE", "PLANT"):
            continue
        tile = _tile_at(farm, position)
        if not isinstance(tile, dict) or tile.get("kind") != "WEED":
            continue
        active[actor] = {"start": step, "intended": list(intended)}
        unit_actions[index] = ["DIG"]

    action["farmer"] = unit_actions[0] if unit_actions else ["PASS"]
    action["hands"] = unit_actions[1:]
    return _align_hands(action, obs)

def _fr_state(obs, step):
    seat = _seat(obs)
    state = _FR_STATE[seat]
    if step == 0 or step < int(state.get("last_step", -1)):
        state = {"last_step": step, "due": {}, "spoiler_score": 0, "prev_inv": {}, "last_action": None, "opp_shed": {}, "opp_plants": {}, "opp_animals": {}}
        _FR_STATE[seat] = state

    opp_idx = 1 - obs["player"]
    opp_farm = _get(obs, "farms", [])[opp_idx] if len(_get(obs, "farms", [])) > opp_idx else {}
    
    # 1. Infer harvests by tracking opponent board
    prev_plants = state.setdefault("opp_plants", {})
    prev_animals = state.setdefault("opp_animals", {})
    curr_plants = {}
    curr_animals = {}
    
    for y, row in enumerate(_get(opp_farm, "tiles", []) or []):
        for x, tile in enumerate(row or []):
            if isinstance(tile, dict):
                if tile.get("kind") == "PLANT":
                    crop = str(tile.get("crop", ""))
                    yu = int(tile.get("yield_units", 0) or 0)
                    curr_plants[(x, y)] = {"crop": crop, "yu": yu}
                elif tile.get("kind") in ["COOP", "PASTURE"] and "animal" in tile:
                    an = str(tile.get("animal", ""))
                    yu = int(tile.get("yield_units", 0) or 0)
                    curr_animals[(x, y)] = {"animal": an, "yu": yu}
                    
    opp_shed = state.setdefault("opp_shed", {})
    
    # Harvests from plants
    for pos, prev in prev_plants.items():
        crop = prev["crop"]
        prev_yu = prev["yu"]
        curr = curr_plants.get(pos)
        harvested = 0
        if curr is None and prev_yu > 0:
            harvested = prev_yu # Assumed harvested if it disappeared with yield
        elif curr is not None and curr["crop"] == crop and curr["yu"] < prev_yu:
            harvested = prev_yu - curr["yu"]
        if harvested > 0:
            opp_shed[crop] = opp_shed.get(crop, 0) + harvested

    # Harvests from animals
    for pos, prev in prev_animals.items():
        an = prev["animal"]
        prev_yu = prev["yu"]
        curr = curr_animals.get(pos)
        harvested = 0
        if curr is not None and curr["animal"] == an and curr["yu"] < prev_yu:
            harvested = prev_yu - curr["yu"]
        if harvested > 0:
            item = "EGG" if an == "GOOSE" else "MILK" if an == "COW" else "WOOL"
            opp_shed[item] = opp_shed.get(item, 0) + harvested
            
    # 2. Subtract Opponent Market Sales
    market_inv = _get(_get(obs, "market", {}), "inventory", {})
    prev_inv = state.get("prev_inv", {})
    last_action = state.get("last_action") or {}
    
    our_sales = {}
    for order in (last_action.get("market") or []):
        if isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL":
            item = str(order[1])
            qty = max(0, int(order[2]))
            our_sales[item] = our_sales.get(item, 0) + qty
            
    for item in ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "MILK", "EGG", "WOOL"]:
        curr = int(market_inv.get(item, 10000))
        prev = int(prev_inv.get(item, 10000))
        ours = our_sales.get(item, 0)
        opp_sales = max(0, curr - prev - ours)
        if opp_sales > 0:
            opp_shed[item] = max(0, opp_shed.get(item, 0) - opp_sales)
            
    # 3. Subtract Town Consumption (both players lose inventory to town)
    for item in ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "MILK", "EGG", "WOOL"]:
        demand = _town_demand_now(obs, item, step)
        if demand > 0:
            opp_shed[item] = max(0, opp_shed.get(item, 0) - demand)
            
    state["opp_plants"] = curr_plants
    state["opp_animals"] = curr_animals
    state["prev_inv"] = dict(market_inv)
    state["last_step"] = step
    
    due = state.setdefault("due", {})
    for s in list(due.keys()):
        if int(s) < step:
            del due[s]
    return state

def _town_demand_now(obs, item, step):
    demand = 1 if item != "FERTILIZER" and step % 24 == 0 else 0
    if step % 4 != 0:
        return demand
    town = _get(obs, "town", {}) or {}
    for shop in list(_get(town, "unlocked_shops", []) or []):
        products = _SHOP_PRODUCTS.get(shop, ())
        if item in products:
            demand += 2 if len(products) == 1 else 1
    return demand

def _future_target(step, item, state):
    # Generalized: If opponent has this item in their shed, they can crash it next turn.
    # We will front-run them if they have a non-trivial amount (>=2), or if we are late game.
    opp_shed = state.get("opp_shed", {})
    opp_qty = opp_shed.get(item, 0)
    
    # If they hold it, they might sell it next turn.
    if opp_qty >= 2:
        return step + 1, opp_qty
        
    # Fallback to normal V16 self-lookahead if they don't have it.
    max_lookahead = 30
    for offset in range(1, max_lookahead + 1):
        fut = step + offset
        if 0 <= fut < len(_ACTIONS):
            q = sum(
                max(0, int(order[2]))
                for order in (_ACTIONS[fut].get("market") or [])
                if len(order) >= 3 and order[0] == "SELL" and order[1] == item
            )
            if q > 0:
                return fut, q
    return None, 0

def _pickup_reserve(action, item):
    reserve = 0
    for order in [action.get("farmer", ["PASS"]), *list(action.get("hands") or [])]:
        if isinstance(order, (list, tuple)) and len(order) >= 2 and order[0] == "PICKUP" and order[1] == item:
            try:
                reserve += max(0, int(order[2])) if len(order) >= 3 else 1
            except (TypeError, ValueError):
                reserve += 1
    return reserve

def _existing_sell(action, item):
    return sum(
        max(0, int(order[2]))
        for order in (action.get("market") or [])
        if len(order) >= 3 and order[0] == "SELL" and order[1] == item
    )

def _repay(action, state, step):
    due_map = state.get("due", {})
    if step not in due_map:
        return action
    due = {str(item): max(0, int(quantity)) for item, quantity in dict(due_map[step]).items()}
    action = _copy_action(action)
    market = []
    for raw in action.get("market") or []:
        order = list(raw)
        if len(order) >= 3 and order[0] == "SELL" and order[1] in due and due[order[1]] > 0:
            requested = max(0, int(order[2]))
            reduction = min(requested, due[order[1]])
            requested -= reduction
            due[order[1]] -= reduction
            if requested <= 0:
                continue
            order[2] = requested
        market.append(order)
    action["market"] = market[:10]
    del due_map[step]
    return action

def _front_run(action, obs, state, step):
    if not _FR_ITEMS:
        return action
    private = _get(obs, "private", {}) or {}
    shed = _get(private, "shed", {}) or {}
    due_map = state.setdefault("due", {})
    action = _copy_action(action)
    
    for item in _FR_ITEMS:
        target_step, target_qty = _future_target(step, item, state)
        if target_qty <= 0 or target_step is None or _town_demand_now(obs, item, step) > 0:
            continue
        stock = max(0, int(_get(shed, item, 0) or 0))
        reserve = _pickup_reserve(action, item) + _existing_sell(action, item)
        quantity = min(target_qty, max(0, stock - reserve))
        if quantity <= 0:
            continue
        market = [list(order) for order in (action.get("market") or [])]
        existing = next((order for order in market if len(order) >= 3 and order[0] == "SELL" and order[1] == item), None)
        if existing is not None:
            existing[2] = max(0, int(existing[2])) + quantity
        elif len(market) < 10:
            market.append(["SELL", item, quantity])
        else:
            continue
        action["market"] = market[:10]
        
        step_due = due_map.setdefault(target_step, {})
        step_due[item] = step_due.get(item, 0) + quantity
        
    return action

def _is_sell(order):
    return (
        isinstance(order, (list, tuple))
        and len(order) >= 3
        and order[0] == "SELL"
        and order[1] in _MARKET_PARAMS
    )

def _impact_score(obs, order):
    if not _is_sell(order):
        return float("-inf")
    item = str(order[1])
    try:
        quantity = max(0, int(order[2]))
    except (TypeError, ValueError):
        return 0.0
    market = _get(obs, "market", {}) or {}
    inventory = _get(market, "inventory", {}) or {}
    prices = _get(market, "prices", {}) or {}
    current_inventory = int(_get(inventory, item, 10000) or 0)
    current_quote = float(_get(prices, item, _market_price(item, current_inventory)) or 0)
    later_quote = float(_market_price(item, current_inventory + quantity))
    return float(quantity) * max(0.0, current_quote - later_quote)

def _rank_sell_slots(obs, action):
    market = list(action.get("market") or [])
    if len(market) < 2:
        return action
    sell_indices = [idx for idx, order in enumerate(market) if _is_sell(order)]
    if len(sell_indices) < 2:
        return action
    scored_sells = []
    for idx in sell_indices:
        order = market[idx]
        score = _impact_score(obs, order)
        scored_sells.append((score, -idx, list(order)))
    scored_sells.sort(reverse=True)
    ranked_orders = [row[2] for row in scored_sells]
    new_market = list(market)
    for idx, new_order in zip(sell_indices, ranked_orders):
        new_market[idx] = new_order
    action["market"] = new_market
    return action

def agent(obs, configuration=None):
    try:
        step = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)
        action = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), step)
        state = _fr_state(obs, step)
        action = _repay(action, state, step)
        action = _front_run(action, obs, state, step)
        action = _rank_sell_slots(obs, action)
        state["last_action"] = _copy_action(action)
        return _align_hands(action, obs)
    except Exception:
        farm = _farm(obs, _seat(obs))
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }
