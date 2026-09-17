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
    'c%0RpPp=(EZpFWfq4g{*%d$P$$<mux7}+xPXN-v<7zQ#yfMBw4vJ2+BN7B=~-Cg}7&mpU><XQRpUES^~7K=q59<qM^zkC1j>u-Pm+i&;&<+Gpf{rKqR%X@GB@Y%ip{Pn;8{eRy5>D~YQ{ny|A>u>-2?*D$i_wDPy{_^9C=TBZges%BdS3iAs^XT1&`(M8Ohd<x@?&*u0d&Z}CPkHpi)9)WWd-ssX&wqON2>9mZcQ-dbzWwm!<-3<RH&5Pu^Zm`U=Rdst@bL7_-H;yc-udPqfB5V;(Wj69{QAe^%eP7YeD9~5m#=Pzx_x^5=x+Giua5(~72hbbmp9Lz?FaV9a54|V$$XJb;j#$BBz}1Q;?;MzBi?<yTVr}cJdM-q@8nW>;kU1!K6~=Z+y8&{`XWl_U8mobX8G*V<D30j-S=O7`7LY7+pm9kwJqQ{hD~Aq^lmx**WUf}gGN4jb@L*5#ZEh&SKR&cK$4f4-D<}0hLfC?7*A$}->{qGywcDNcQ3$wJ)<fx$L$@tJd5f<Gkf{`_1%)76c?xmY5Q)5mshROj{O`!bXU@j&FF8hzn*ru@?4-Dwm6GwLettFfl?f2*ippGaCcgt{IRn(`{U!ZO7rU15ZrS0yG-Kd(X`U#^C1~7J-LMFrr&V<LFiS+%GzF^kNLyf;s5T28k=hM!{^VQ-8_Ev%b#vuyn6cV>A&4726#N;IppeEvO-mbL5as)4%GV4<IOTHyT(K=miY=x`Qh0OCG>vTmt@x{EPdn0AL?~~sF8}huzRO6M^NAlNdU0%wP)oQ_)R;P<2sLs!JA9~_dCeL=Hz*1iUQsUoxmrC!~e=#zcYw1ZICt(YW9@b`8A!Bf`{r3D?5B92ewJbIs-1Q-He1#%7K9TqdG;B_D-}0ybt!<W86u<FS#MCo0ujpZnQAgfCWs_wz3Q2@fBfqAe#k;M>7ssZ~%|6_x;m1FJHZQ^wYODFJAohJzoBMIa$jAA;B*F-Qx_|pMT+aA3v=>=L<)&b*^9ah+lQuUjUPxx;LC3&=fZ$9k7(?_ewV+KQXO&><n`xzeT|&;!W1GF$B&XkQK+Po)Y9LTEfGH=IjIp-qT8jo6?K%)!35+S?9?o53Jyfk-N0n`7ycGFh;wFjgV?*Y}<|*(dLftb3J6Y=(I?BfgK^|ySzkhm^)>s9NYA~^`AU-^5*!**~RQd;`R&sVV*t~s)7}yjk6h=dh!_GzgO8uFaA=?05YaQ%MqtGTd&ZEa#2S38hl(aNs1Qt1QK+Hd}plX-uqpyYY9|1%%Cc#-H#)<f%q;piREC##OBQ*itWIzFLEW^z-8_(eI5}nmQ@_mFLHC-$4*Cr<u_j6#R}1%jTFjM(uLH|+3@S^eSI;ikoM2o2n)MNUMQS~*_P|NDnQLVFm(>JoGXlj8*fS-Eb+XQ`AYtkwW@;FIw5INzk;N_VA|&Hc`_y+XLoRK$KUOzsU35Au6kNwTZFjHQm#tp%uHApM+vt_YCwOJ)CmI#nLT~m_>CBK?P0m+v|F~42%vyLI3SgET<7;x!LCn-C_M-*VD*p>f){?}$973(m-Y~|w6L}+J*I+QiS)rVf<z@7K`v)3Q@Rh-r_%9W^&JGBSmhMyWr!mFJ|BWSvI)ltvrO&um<=apn?mK^D~YDno?6wpqQ^x#VLkB4i|0SaDv>*qyAAmK`Mdw#mI>nNvDFE_JtUvNX+bk1K!*oHA@vvD;k5nZqKPPa**c)!9=Iu7@g-^SwR=7wm7~)#JW9<jkI%6Fud1u!RCcwcYQ?)8hY82)!+v^up5;DQ<x{*xeE+us3f;cp!JyB(2)dNsi?=<D{9Jo|I0Mer%tvq0m&by%C8k{`SwJoV*7#_yz$9G8Log!dHKZonJq+zxn}?KYAV^i%M2xVa`O*2)K@>^<pz1Ic*Wer}zbo`Q8fpkf8Cx)$yk(z6!a+xYDgEoLph$FLp0=V@^AvMRlS*2ELl`UiB(!3r>)_A@>OHmfkgLZEO^z&i{%eR{37%~FSRz!aXipw%h%~-&I!x|9vY(?%8){9!TQOsBw`LK&vtgA)Z;rk%qsGA5zV&N@`wB<2Dc6&y{~8UgF#?=v-nb)KirxA(#-h$4_5F%ByPu#}!lW+L$51T;Yr^(p2pNYx-SDxI2xw3Vb{yQO2NXa$^|)n}(IIj)LqHX5WkGN<>Y^g@yAP+rCR7t)r<_=;>^>ggM1_i3_&Gd#lNdN|)1|w)ew5;~%#Wi18oc3-A;-14sFhOLwziN9y}ds^;KYD@`U@TBCugkjHqwTD&N`4sxuVvkh@*oZ$M2oj$|Vln$nyqpH4noQbf$MN-_{0#eNVwe28bLt<_~n72J!O1Q`7dkUpNLPW7tS(2fB$|V(J1L2+mGIfzCyRFDtEJ<~t95(mX|t3>^b>_FA2N3OF?FUSsrH1k4tYlJYz&?bGF28keNmFKx7OyUP))2^K)uUMzF}^EWzBaXu}e$cwPDSGBI=qAv!cR0)eFi`8@A#fUa$a#}grL`4!4F-3)z!owg<xk6<>x-v#o;h!|hkOTY5^>=y56I3djoD`G_`Gw9`Yh^&fp@65DV_Kj|n?h^dnJ8n=dM#vcCtuPVMj@@F9HJ%UJbWMdp@Yh%8Zn(`L$p5+%2%Y-*xyBu#fX_bGlC%uD})iUCxYuJCg*?XkELc7cV_+jr_cWEx^H~SG0`!I09QnI<cb|$B7(rl`owxg<ZiEMQ@WrQ!u4c}k&N5%LhsOcEf*<9z8=%_jyBUBqwkyd58rsO?=|$}#51l8V!4cy+lIm6+E>j<(M2O)XVdLRQb=W~hEkM$$JCYhhbzid##Vp+%Z%|WX4#5bT?9M9$w5Ym8dYHetKu?k>Befe@DR=F5Uw&ia>EGjng}yV40(>SAc@BG$a|H#gsX*@W%%nRa<j#VcQXb8AYsLm@v;h%YN7L&bD=XUrs?nm*V5$oCRMToQw2!e<E*{suu7ICpjLR4keGDRSpPW0V~_yb!(T*2ovViIXQc@8Y!G(r^oT`I)7p@DjP1heK!FEbBEAp4)(4zDq`_=XtVN;OF23{PTD-r;Anc~e+VOYc7b+#3-+^SYR9$Y7KtZe=RD9|rFj@Sgv#w6<kwkDE!=?xX+xOc}LQqCc^So!iO83P1&d0;rUu9<qn6ADvlpo!a<b={kmQO0Na^lbgj8<40Q38nE0|OPA>>KgIgXu|7(nV*~0#0kLI0eZVC&z;F)7$x5c41KCHgkiBi!qBFy}?`M+-&`3!iowj#7P4U0P_@l5)bbyrLh7zNa$!{9&HH4KtMV^dJM*=U;C2IT-=4~B8;xGHW(yps-~AAt@EFFg4e-9(+Xu53?&CsAcU;O00-pIC(mRG2aHBsR0tlKKs6T)tPNE<9${)E0?;HW(p2U=1tzaWfQi(*5704)?UP}$GR<&g3tO&6iV+YKATC#UT2;zRsI@uw5|2x**KHO^QbFC(Ye`=Kh*ykS(RUoMB?tUP<11P;CFu^=N1~*8&uoc@a~>6-A#&pcphMeG<x$Eh6&lw*4!SFU6+XQZzRF}lZ#dHzHUJWX>0?mS6fE7Y?~p4Qcb7Wtv_4}=Ri4<WQ66*H?8%M=Q(1yMe}>^uwIN6|Y@LZV&W244l6-{ZE}r32dMThDZM(zQb%L}xsny@*QoF7srY@gsMogon|ECV`)nttDe(b6n7L8!mHt3jJiSD<5dvII6$iCcnRT^bL5P(QIp2QS12*yGXg`6wacd?ayr<BDcde054La|U4H!4QDDvrUzs1U^~OsjTWr*9>yg>dBmUw(Nw+r?mm&BHKp-cQEsD8(N;`>1$RQa}#R8JpFr653aJl`|GoxP1UdVOAOTQ|*vLIpTm~w&{2#MD?Iv`WW75?K1>LWJ8g@`l4iWNC6Ag6f<pw-bPyrL$`pA5o|;Oj(jLgfplf-&RE=cmU^(n;|l!P<uUr~P(Up~M>M};)yjrg=D~waC)j%1_roDpjG_7dV)rbI)}EX&k8#x*Zcxr77+}ICH_ER_389%9!sev{x$U9D;`jFy!KeuP@G=5*EV*MQRsz8%tKJ=rk#$;7V5jLlm7p60>VukznkU*zT<q;_bo);OAdK@_&IMS}VWODzw;H(@TVab%Yn6{5HThpC+KG$ru9F)rceY48I=|Dtn-`tP_vh?+vG79q3N%#SHM8=|6_a*5sipAw?cv?+>SZ?v7_o7lhA8A{eWB<1MYaY@DDVCDY`U36&OIq7j|v?YRHiUVu672YGPFfHc4r9mxV+S(KLAWMN~o@%04L0IQddwxaz5htx2p&#V2#kuty$7Fy*Yy9LhJgC`KBTJ$S*BQ-Ts)iV_a~_N~67n%rF?Wne+V{ot&`#+qLr9?)#fDpW>cV98Z4}B>Y>2w<?y$XMCjgg?W^(COUQFs~v8VgR!CwN1B_qd;@XAQu+e)<#m;=%!bSz2k|BBkz3R1CULFH!D!F|=PCuI7*7AuyuDWElVw)HzVvjM<aDpMG{lx!uf{)U?7Rb?l~UVB#Z@eiYM>ytlSqfEWccz-Eo~Zyy^5Kcd3V*uw8NasF%LwdD^_z<b6w06%@Z;hqN?iqb~GZlr0L<W6AzCFJ$cd8sYqxlQ2d>c)=TX8qXT=3_NugZ1M2@_<4hmdy)Zax_`jy|fK0R9sT8%1tmlfch^%eWzkYfx!9%3rmZ|HNEkYAJal)shm}9pFBHT_d+7jEnjC$xRW;|y4hPd;78EHXgez!xYsdgVVI;Kx;8RZC7{5RXSzSomulhAL5DQIkMf)q|cMV}Ood908EE_6HYYXJHr3E$;9@A&&RZlF@ZAxhARzo+=!9KuN&dh~B=r_{rP+8>mLEJ>xIeO|^T)7UGj%4|oVUBEl--xW5K;T0H+PpvHd{Y9%E^{!N0+l%Y9aI2-w*+YkLCg)nA$>w$8M}-X>eE72%pdfJzs;g{cfsEfWJS93<<{4X+Ja1%21yIdR%?g(-2JK<yvs9W;Pudu@d@HY`-VI8M1v)|(uQe%A@@P0nZ3{}|U3^~JmngPaMId0ZU7rx?w+gI5EIt;{i)Yi$78u`xJ0sQBD7DS78&O<Bl71tx-N#MgZ2G(vk>|8@H+8fE8*sDWCG0vlZkxfl)#Yb=mbmJHZvxLhEntXL3DWgJ9zVsGrx(a1E0W}CuwL)a7DVV{)IUUG(T>vD@rR+k8CoJoLWhRA!u>Jeh`Q}ekIZYO%FT>^&gAtVj`oD6a+Um^R*GLtLnRp;?5#or2xitM0vy7hFgGe32S2J69_OK^fsz#Hd3ak*_4DpC3Xm*-ab@5niwgJ(J9I&p78JElK|ozGqOJlovZ4q@Cwc^jL74;5-_}#N9L5NHmRGn8k<K2rpJ1Cz2cnn_zRC871U*zg6W&z9FitI3WUh2|jKnuorG=?&Dk-0?h~QuZ>4^B$iL~2mJ&;$<EZ}WO`avozKIz1qFc}bu7*D<u=R@(`3N)X<JqJ)g%~99_%@ARzEwpzr?VQY=QDlmn3^mNCsxYWJsIq*M=uB>c?h34QLok|wh$Ng%6S0>{lsuyPlN>mZinynOlk8xU`M@O@#B?$Ehw&t6F+|^jgJrmX3l5A`_7JrT9!7dlQQ5`<9-mL@7=ptuO6BVLMZFd`sPbvSZMVPcf|ky$wMSqtq~~0-+GRy|g;L#%SmR|)6!PI!IvIRDVcN0Hf)2dOe9wMNOA-}a(458~hAJ8<1pZ6q_SPgN6|Hv{OLw)k)E|P?M`X+<ybo{^6&GzxF^+OA^o3ZUx#aQ~+4*jxh3$e#Pf6?)uch&Y8#^Xi54h&3Kq&MQy_CVnA@b~_Wv^A`ERmrIJ@TFnl_qJG?dFeEx5^VdLgB9;b6-HK#7GxkZ>%$(W5HxAfrcw$z29k1btGIxN9j{-<5a|0<zpGtP0@I8A3e_?6b4HgO*5@#rP=76T{P<~4FAGKUxhf^xgvBl1r?d1t3mee;!@nZXADqJ#Y(ydQ(+!`&0J%L{TertNPc9Y3=j^TMd}&PvC!lb*3_)!@2o74@nZG7KnA_Ilvk5P(qexF-2HjZpa`eRln}dRUdi51j&fa3J(R7m?y^nx(&4v5Kb)GbTXFIo=yJ{1E9V=cM2#;LE>9$LEBBW~#Vi6(;2?7xa$^%KCRcENMr9qk=R++lb1P;`)l9nj1YLfWkcK5#yTt{(lsQwe?J87bR7!?@`kAqfqfKL_Vo&?2Z<+*cRTgHb;xLo*Ahx+E;y{h&p6Kah5|(XW!p#d!LW5O;vMeT6pG+neH^2VDD^S`kWq%FqS~+!lNQJ8?i3DT%0c?(sCK;ejgpO)Ad<>(6uGr!ZfEv4Rb<B2%Wc?wEg??(P39kb)6Ld#bz98Ig9^&pxg9?B%&#4_d#zP*f5u?Rjt0X5Ncu+|xS2PqRtC+WgHjXbsCIYpf<}I~P_1*A^$rd$=MLf|fv~KD1F4A6|GbL5RHl`IvVTshRxfOT9?30qCF8kBdgr`)lT2$jqkS<cSMM$W`)wTzIjbbR>D?;?o)5jh<UHQ+%yliessRt#m&gCX~g}2D=6SL7;P{AG*K$WVx@|G1GXI~`aE}N(*4C0!+YAOVg!_X+{DG{yQ6*{6y0!!W@MpmeRgv6Y%&R)l$gLF%YdETk2cq-jw<xZi(ttC%CO7K#WGBb?fbpoe5+Q4tac_|xZ*h8A8Dq`DxycmV+bnInh>L6{u@=(=!=B1Z%^`OK(=xI=2TvA%$lgK_;Aj?djqG=};%oNLY&uu&ya-+%0o3`yT)z|Er6A^}wG6&mZoP7lVP_N;!$ifZFEj=o^WU97IGumccN}Zsdpdq5yAB(N+s;HI9vHswIi_C`r{1#@M<a!B*!ZsfX8(J8W$%ToX2+4!yEgu$S;la_T^%)^=(+DKBd&jR&GippjfQ;h3^>V4P%FMIPbo-`6^q8gf`J26qa_Eg)$JDsuLSt?dH(<?GX02(`^d+pv@9?%F2^mUM(EP2~ca@~H2AX^hnfSU&z0QFR)$3JVe=5Mv3aDtYQ>hNFf_LO$^lrcA2#3y)OCiiSf6=*AD*-lg_!>VDZi(AtI9&FdXU~6lZ|cjfKMM|FkIv>hXCAr1E##w@(M}CIo2r|5d<sWn(Q;=dU@xUfV9`w@3_U}Kd?DqspW|R6+KL`&_{SYnAH<0olRJWUDuD4hp${TrbHLVNP8?+6_oGd#Hf*dSh2FuQoVEe4I>2hiMPorUcC(lqDi~R+LdPD}X4<a(yJ+a=<#}o5ji@P7s07Z8JC%qt1q1oqczQMO4!dhxbVo}i?>{WBvUJrb3Gubeb`OI@1PP{4sTI%iJTOU>jInoF+^tjTJim3ST%ZOA|5SK!!%!n%vaGQtD~=MM;)o9TTa<c|88aQ%o^?blBX%NCJFjv@gK!|ih=gh`EubLp(-*Bw-es$hQrH9WyKCczyrWy0iZo1gAV9~^t{H>~S@Exk;y@;RFR$^ehvr*i!fBQ2aqL076+Gdn3~4#^820FMVL$ofg;Hd9tg^o7rANs38<zVm+P9AVIDy0}qVp{3>ZOP(wYZO;|8yZr^3nQn?y5UoIx>8UG-Ti!xSm-wDTygACS#7%TGg3JdPzq6pej9682=odF?>K(x-6&-CduJ^`@~gRIt4Qe>^W+klP7)8N)ijB_(mjFqkzEb?;WpZ!Uz=e3AViS*J|~s@^JxLv;wWIj6wvCc1kHSz;~@V%RK~TSSTjE`<EB)orqo%YTk9XJ*tA^$VL9Gzq@8qL3je_4iP!0nt0`r7CPpOBBXC$KYjM(m$yFHtJf(tuuuV+PYN}(Xtyv}c>9dUH>0B#X@!xx%VF)y+Dw$u-o1=%SAH@_d;kqv=gVW3DDcfwo!g=B$97M_5qt*nM|pHklacd$ibf)MSQadp!W4}IR5p^*$uLB(E}Ld>$j)UV$%=5qdt@fvEtA==H&7W^Jc&q%<Hox8)z(4SbJRYuLd}R&a$EaCS-inGoKEg)R<4Q-L_~qEJbY?5!PB7VPx9Q#Yfv^ok|xt0I5n0lRhLP?F=u$@x$m*7=zg;tYzOU_9`5$w)(Tyr(AZ_4UX%2A-Fqd|3m&J-qRY5V<J7DW?yO3i3`}cmS5c5F7y)`*oDo<`(-9yTX}>`S6cPLs7m&-a+6*EEs*1GCVN=1KNqN<@;)gg03FDD9gqJ)$6Ze(DfoN3cVp&t$le^7A3OP!<yS0{6Tae{fx}5>J>#+lEDhL2<mBQt?N=|xVdOc3)hgc9FahCb%T<oLU*cq35^=}m33XrH@%O;dhI{p$o@OC{4%~ZouxvN<9lYT_U#l^U~^~dsjmBAyy8|9L-4_41;&RENDMEJ|hSZ%6Ubfo6DNBDtxXJd(zN}gGH*y;(eV%wuIvvP4S))h7c3Q8(Ekj26Kaa{E8EXOw2#X@f~#skQEKmD<zhHgK1F|0Ubjtt}-=tf9)vl0FrM`!!A076)Gqg}r=^n-jMQdtf$JRJ3+3NZxF{c6~fc`RYoT8J&O?A|=#N9KR?!3$swwln02XJkz<6dF`PKumVeN4=m=BOdDC5`dzNv<o8`Xfd9N3I^eSdQO;!QwksxAg<a3lmN2w-2aMWEvWRx0Q<~R1p{qC=)qbBED4FGR&uK)!pFxcEi?*vBc_X(R<w6VjX#P`l>(cL<(!4jqtpRyR{o)qw<053j^dGgl0zRvqY+7ARS1HA1T}G%v3|FF3{I4)MO0N@0pB#EhYE5ZY$J-d3pd9czb|lfY<e0k9iNRC=@r;rqQXb?LhV=?GwB~{Cz{sEm8wR5&aFuljW*1ESi1IsjL$^(2xZI-8#MHEH}g<A9Y>X!^G0Oi5j{UQG?R9<nu!ppBD<<m#d=d_DBYq865bc8M@NmJe_C_h4k*wqeP+qA%+bQ2aTd`rLU<Q2SF0c#x<H|I**NEbP`cc7oQiOqP905J#@6-NuzyO48%R^c?@#|yObj9Nyh}n(AHq@5?#;nO!B#jjJgvLZ#z%cZ9F+tU|E)9dsd7dO6n!ur2-ONlazikN&&&NfZ6t)p7M~O9msPq@r~WXAIPB)d(W9<cfaqT*%D+$i6E)g41`|2<Iy1--uitu3okY2A3tvvV4iSK&kceE59M3-3xCO*iR((jkq`;AbLnkkoATK;NHAZhr<=J+&vQ}z}H3;L%KRNL8xD0M*1i9(a#}sX%f^)zOE+dV)%MwG2E86IBM>MA=as_nbd706BCo#giRMgxQ8NAghJe!NjA8A)OEzx_sxxmlNFmtD%HV8t}0;bO91{2HirAEDW^=0Y`WC_6{<T()@Q#K$EBYW-m@<Im4+`a!j?P<F9m?Gp51~*bX8lYj5aq6HLO>^vDZf$?n$3U<&th)5k(lxA<&H<riMcBFqU`Nuv9M~Xe>J~(Tylmoajp>uZp{qj%(g~u_!E)wXIj71Xn=kIq5Y6NWQIfNf<68m;a_1mgdkA|(RAWu0>od#-T(=ksf0}DZ-+eN{=MGKoR56#~KM^PHfjXDQ!>o%0+5DRx-A(bvi=(w!F`CF$7;fU{tMRVr<RaK=eg9s;5fj;Dp{|uOCk0C84roLDr3_0&+Hx7_s9JsTC!9E<QZIG3j2W~NgAWg9%h47t12*uS#v{AHE|I8!jdmQfHea(uY8liDYp1eX72A*zphQwa$y?QY#NXhfNaw@LWH)pf^L=T6R4zxxa)%QuV{2G|N~@hF?h)1Lqib@c@?xIK-L5_)AwtU~>?aBO8}PPVnPkknM|mcYt~pIpAd1myI7|xsZq%y@(g*7@0;Q-W^7nw)Me-jCa3)!G3du#Y>|}pfeS6z~f6B&HQ-Ph!dl?)TPvA&y#eqzN32mIUZi00t&KpII&5PCpMZK-8h?lo;^JxzB;HEPonj94}0MJ|*aV-h)mx5~4ybM`@UD}B*ET?&mggeZcPb2Y8>@7{JI^n&yjsCCNSw62uy?%x2LTqh)m#b4xc44M%L?}>hK+6e<DDkQUzE-K9sMPeCwQG&;S^jct>~aUv`jqXo3OsvphSnx%I?>l{!)320d$3EmU+8a$xJ!C2bCH3<AajROGAtZ6g~A)pN0!+dR*jPY?P%;d?2*&oTdb+~gJD<m)3p8qss?T<uOc#B;#>BidsAYG4!1+&q^Yslx*6ms_MU(gC2r}riqa_i#E1_kX>c>4yarp@U$z(%P?TCiIzY#ce2!6z6)D;RMarQ%RH`SXjQD9)JDa}V4jShds5zM{SX`!xwG#ry{f800Pw7WhBvrD0Y<P3bqFW=UKo(8%LzAZBp=wfxyoMb7)|Fy{i5+sv+JskucN-V}a49V=92i3?f+`N&NAJ^wH7?E$X9#N(BU5}#2AG$z??+4h<^&HeXQLs^b^2p8pHA>BBFXB|j$(14pNST2ACA*wG8;1gzl(nF9RLjH^mTRAy8ck~@7bMNnwFOR<ESk0!SG8jB(GE((qwuK)z2S26Jxf*E->HP8CB6aL)m*7l1h3L9tzQ@bSElr-00O+?j(_(sVKIb(rU>^ArL1z^rtSa@1su%5B&Hy=O#mU)z%g97`@9>#O8y0+atudMXj2oo>mBZX@oDvi9`iWCM73>1&X_Gf!0PLK$PIDz|<31_d31CcuOj6USpaUHNOc?%nuM@z34;Mv8zgEMeY&UrlPj!v&X1cZ{OS`x{V73!m(@GQ-KT_n3cMXp#-%c8DqPh&4r~dEAay(^+>8{D5S{gRjyW$<<u8!lH(<&b;~kvGa9r;I;|vFE?BFDms)~iHk3*P`V{r$gJt*5N|_OwoLBWZMaMZpwr>Q+&ZbXVI9^iv;Rv{ICIV@2dHEN0LCV+5OQ7T;cSo0JDeTb!7ii`>y-TqFRlL<ZP|MP8_$zotQ{IyzA{dtgXW+^G^dT!M9ds}pMJi^zEQVJSc0SM=HX^9oV%WqVRJtH>ky4#Zje2eNhmKrG4b3P@S?<U-q+KZ1sntcggymHlf)0=34P@VofnkPEw?8tX3%91SBRLoPQH5m9=sP?m@7imHXQZ8DwQXz@DJv$#G5S_PpR#}{>!437kTqTV-lk)}lH+iUnmKR(Blg8`T&c>)>A3GDpXJFL)U6A1i?S@Bh@r1pZ5X4tRkY!(#=ljBQKXeKen+ARc@rG3)r!^0b?<N!Sx_AYG*G*1(4~SZG_Z6f6~twtP)4Qsk907ICkxSUIaRN~@t{P8_rfXfFSIuo=FF$01)wEIDz!DsRq{`H&^dlmn+&kwT&CTDREBAst7={kk0{PU5(a&0-%KF#7xB?B&R>qGf|`q?lSY*^XH;vOJDd^?5Mu2QEUJPP9&p7EjZdWVhHxv0Me4)pcby;K$5whtbpbd{6$Xuxqf{5gggB>5;51jgIt)LVcblG)m*R29Y;a7A#WsRl&@l^@9i<rD`3~vXhDeAijTld8f^pmcdH8Jx-YP(h#z-ypm9?p?<4TNBY;#dq*Kcb&Cs*7<HWixWW-Y|b4l+PqEm!rs{0R+Z<$XghR1iQcelaYBbd(>YiX14dT+Z|nnY}PtNf<LwF|MY5Ke=f1s=vRQ0Wui!UbXm>)32ieZwLO~<GLi}Ab*Wh$OpCqTi{z{#GUFRl)el;V^R-v_huDP=PCC5YNCC<)QYGdltXGakj{TGE|R6#+=&o$MHNB3`Ny082Lw-uiU')).decode("utf-8"))

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
