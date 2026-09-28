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
    'c%1EBO>bOBlKd|^_kpBDS=<{facp5I(V(a?W(~tIFtb=-F?;atZL$A-Np-)Es*H??toJB;fjP0!?Cw{URh1u+ky$_e&x?Qi^|ycg{kIqY^3#hSu0MTx@$=!uzyJE5fBUb;Hy&U9<JaH*<M03d^!k4f?ni%m@$Kio{_?~9-Mi0kA6^_@{P_LN_2b`*v!4$?z4&x<d%L`Me))6v!yoVNAHL6j`TO_xH!q%k$9eHIjO&l@KU_aO@$KD@k7EdLfBOFB=7*<$bmRDR_qiR%<DB2W{qyG^PCxbZLnk3DgI>RCKg~oreegJx=8>zPW6%2b^ZVO(zdU~A;q%kforfJ4pm|vLD{_Lj*Kco(`GpnjzKWmo<ISgsFE8F+iz%Hx=}K+>;a=`>3xB$~dH4AL4>z}WAHf#s<;6$vIOmTK^RFfEbgQF=blwkX5-iwC;Azv)e!PCTx$j?n5fc&npPok2JYo6r^2?L3t-WeZ@wgwF=gupd%X;}tE1~kD$K7TLHh$<RzmXMge#n&n^1pbVn&(c6In4X?1FPpvDiR2O(k|-}gbn3AH^@6KcNBB~d?n_W1u?Vrj^ge<y@%YvIy1Q+KV5!sZ{eRu@Zo&L#}aw#gH~{1uwa1!c}9Vf1w9QwJ+>gw<+mMy0+X~!p#7stKTLkEdokn-c|NE1bAb5+%cw0(KT!DAfW=;hb^4$2E7AVW-#z`y`H{QZ+ncu!zx?Uu{^9-Y`+x0K-26-MgB6Dt`0>eaPM$&cHavHyC}#E1$Mb$j0-s=9Zm#<kUQB84s2YJ)>IG)f<ugql4W{hqn&~vg;3Czd#su@{1WAtRmE~uiXPDspZW`~bX^wkq=g}_OVT-O#&fSK6PM&q0@3H~wvT1F0wsdiY|2dSpwLiQ{?R}=)CFCUSEyYuqp~;-PXpC9tZ9L&DJV97$_B`nZAZUpFp4=%!<Xs?Y9cm_Cgqg_k+0s0@2qkF($8p<etqn{9{EgDw>O|7P%E==D7z}s%!SAo{|1ySf5Gl{QU?d!~#61stLttyK!wN8R!dvMzZ`|I%4Q{ML?q22V4Q$7&DKKbL5p%qtV1qX6z*XD8HlaEgAc|6~><0lZe%chqIuQZHaZ1;O9FMPrQ52k&mt}B5dM7MxV!dK+grVee|3uhm?Xu(<g6gx1nr^S>ASfxCoa{x(qJtk9vc*y6alnf#8nctD(Pj7VVu(Ue&s1h+5XI)BOBbh&jd2;|jka-}@WRt-)v;|aSl(}WMMOQOlS35Hi4&NSeVrFHH*3oj{7Sw-wWaia8-k5P-qK6|QB0RWw`o4~z1y_i`$WOj$oz%V-eXYE@F#GCe=z394Y(Q1Ra<^HrM<}Cx7TJ8F34Y!r%A8F@$sAojre*Q#ii`~UH%S0RoMaD=7K%5=QV<?fuk{>XAAt0o<fv*o&_3n!Mc20(W4U*&mCLm*ID!tgY6Nh3ScJ#o>tl1%rXbg3HP&hc5$O`lI34UToz>5Y3j|*>5vFzUQwEy8&w<tLm;~ZOk|%JW!^u{N}_Zv-AayA5zk<<LjcihLspdFo!~(RJmh3?+3&dnuY>o6SrBwH{@e!Xljpp<zx$!;tAL>3692m6o^t$jTf%+x@$%Sg^U3t`bnf6qGYQMJSv@sHmzNJCW>3e)_8uHO9-wfhpM$eZ)RFcUEwph{9&rA06w!8PHX~G729F3CVJMsZz*##*Netx*YT>hH%Py1V+bPiqE0g}|;r{x^Z*T7J|7yky>UrBH22c!<%`4E*A}qR^z31V_5zhuD$C~Tv*vr!{(ExY**K1tyT-+JCkFt`tVBvQGV?bIBY=SXohC$$i$Y!=feI0k&m>W~&5X2my@Fnxv#t$6Ikc(nGNC_prj`N~QhCV)#nfH_`ZOL?5b(ma{%<OJ_vyn77-K7II|8NQ&0q-p_inVjNJ{PGsgx}KQk0&$w2Vm;)e`=nK^Llsp_~*6Zm`|AX=?i!OtHLYn4)g&(8B`t#&2_Dhs^d6cQv14mn;O<Q<3;qzRFuOr|3H#lAanmRdXIKroK?tgfJ6~+BnZ=_SRdf{l94_SMj0b{P|^z`_KSTD*@7b^z*Wwwa*HkIy<D!j>hm%=H*oz{lw+afI*b7*EQc_1=tghAKRt7ThA?rUz+UvF0EXidD_!M-!NH@+3|ZZ(i*n%L=?PTo5Upva0nOk5ZuVH3OkzatQzpWUDFlDlM?ITX0Ht0w8r?w20SJ`osTYaEWR+Z!lG<m<N--J_If^UqQiO0ldUsW-M5aOM0V4||q{`?)p!^fCjfL~J$+&oHN0XEFwHsS0eCYC!(a@^VrVxC28*olu$QUw<-wxk&<`%_rCa+-eT1h{eF`jJjSYz15JSxo_@a-8&R}!I>aO;RHue8Vwx4m}Ury)M<#4Z)e!7owYV1XVjuZ=4u!R^sVExMd};LM`0!)Pkn9m)a4KUS8Cikc=8=FJtYQEr2x%!DdnGFkFwT{yGEUMXwOj#mw<B2FPV8%7POkCKBxS<qakapZE64kop(=%JwKB@(Z5x2zTwI5MIq>Zq?#<yl&?p1BBv2aR~*jl<sS+b*Q9r5*Ef)5N=7j-a14v}?YCXNg9T)`)h(8QoucP<h>1nu{5##Y8-1KcLO&-kF8ixI}Qa;5~~Lr~!DC<z({S)XjmRWZ*4si3{N}=vU~4Rl)M)?O)6#D2G?p&M3IX&lWhv7b89iw0w}oL{nvUUy$f0i%fSD?lP+e{y86>9K;=@TyQXWJ!T;3D9X|(W_JiZddXRy4DE;aw|_omyfnupC&nLt<{aduPLp^&{U>&74PT+IYs@0X1R+40Lub}B1X;d}+B#bK6iUQX{<VUlW4>*fQh$O+z;k4v<JsW^^aH`|+V!c0^wa^4&jClFBM%)4F;up-g9Ib+5Ti_%h3q@Oa?E@S5ecNWfv93Et^?vy`l`;X_vv_X7C=pi2Cj6h1nj~ppT>}#w>5Hr%@Pmk-c!QSW-M+Q5+GwKDfQsth?wGOSSP!4o+Or$$H&bR;Ho*4U%>?yE3G;>0FY&`QxIz&@Iqrc;r#F8qU^>Z01m&&k!)lo35z}}jnX065j6hEl7giMWHAN<vH*HdlA&FCDbB5>W^$hq$QIbpZ!0|8BCDcTh`QmdJ$0=&CHOY8MGr}w3eq^51$sy#Qo359Q4hiSPti-2vKG&nF_1Qv=0!waGt#Xdu3hy4yh#>ycOPPCmT2JsYj;)XrCJs9@M@b#i5nSX78M%Kp3G?Ol#B*shZhZ;P<|3+`Mg0_??W7tT~lFykqwFnzGMABqPrHeJgbM$bO+g}(@$uM1#@>@(5t!uS<)6z@I{_JCs=LTgNMv26l59?hdSnYDs5Dt8Xrkyn5F`Ta3;^os|<GY4pSzf+~#R#@kC?^5NnpVnA-BGs94K0TVLV#)|22Kp;GFIC@#Cw1S*VnBGKZr+!H0bO7OM7v4urZZsMHuFQg?f8N)D75Sm#~h9gBJp|;cWJ-l`?7}6)Vj#sLbWlH(JJ<!0m5VV$arWH7&0{(x+-08tiqLL%Q3hAuIOY&kwFQ;b29!?J~`3iJDW4~-9+A>cpTs`?rGXjdn2l^Q4&K&^3pHg<$QSQE{7A!8Vn`I>n+<x#ZLZ?Ih+l)j#t4cFupT!Ctw6;*=BSn}=G9)@A=v8z9hr5GWL*)I!K;D;uZcev@;;3+~N<>q{-BG7o?Orz`W?s$u3;1AxqTjaLQUY=<zns*Ag#l9mp)b%M0WHi;4*YaAV1|ZV`YIj!{bA7Hi1L|xdY*@WZ0_eyO)%whpixssG$3-NVC&dc4s(Jw!XsoYQ#P7r=1UQ$8ssMD+OV0N#JbKqBzg~2P<r9#dZzl?<FIgN(~^oPoA=6yqvyLd=Q0B}o{V$()yl~h76rF#Z3Ukrukk~8MBJvlVm?{L%u;;WxmV3RNVRj|-A_9|@z><ir20m(2K#FQ=mgI%pdDB=$vng2Md$#4Q8U#OyfV)m=`IkA{ffp&vemFE6qMlAujY&kHabTTz$_Y^w{8M`aRZo_Nv@1L68?N7$iXJ!xlRy;kKKzMhVI-OOq+;>|A8cGz;_FE7tV0Vi(0Lugr0(R5Dwn~I=kmDfsb+6fIgudLD=`JQ_gZ33TGlO@@7RYOQO{syt4@<SA#@Qc!%|VFE$t(O&E@KC|s*PV8V6(vX|)1i?w#jOR#eK2{|_;w@n$xjN>lVX4jL*O1>2~pxs0@YcG|L9A(v`Nm1ojMV{u;$ulb7*u8cgT=5-a^)+6VpKL!dW`n^dR6%n<t@RjD-tLv;Z!&hdmye@T_D{3RD*4%bkv5Y4^V{e--2}F6Fx8nhg}c=(0H9t`@aZ+%$+Fo^euviVU^$#1nl6-Vz+6&@djQXY6?7EheFSTR;AGvnfwRSXZ9cFHDrKIvpu&yk_~Bp$bxQyHy*a1WRNg#2-hM$hTA8$woD<})d&s7OI9Zwf_C^I_Cq+zrSbYUu1-xzRTH#75h_j^(z99Aw_!g{}g<Gl7{6@Y+iMa(-))B3g_oJ$ju)aW{N2P_}6Z5vuvFadh4BY?b%TiM==qWMapbez+5!Z30N<#;>^z@>LijL4iEwh(OY=y0QV1VQFrO(}0COJWd38S5~XW9KAtxYT?tXMO1+QPSTKN&c$(OJZF654R1B8JG7Pz+{}-SR)l>`0QqnJX76!GTxyK)Wa*9oJMsyeYNY0ww)nv&Dart^>|~2C)aN6^qOp;B=1cYkN~kmll}F0);qqwuNGo+l#3Oe9MXJiF^6X*FtO29GQ`RwhUze<wn$-VI#Sdt!pQg4;Po;-K_RKn_T7W=X|OGg8-em%xO=pQe*;{hf&Xfk$IxhLa{ep#?j2SUV@PAzTW_Fk$m#q`|pU;Fuc)R1qo{Wt*db1JKF_K_|uUwz-srM@U7ycL&F>wISw+v$G&9r7?Pp(Aj>q3#V~;4p~_M013^;$1Gfo)WEHr=%O^(c#&sCsLF^k<Mmpq|cb+4>1bs(hDmy<ZhZuz%lGJx8gI{J`u<{<1tjLD?3cX3w?5c(@&)vs2lhNkkaxHM6Y-Ldok!7O?LvmI@fp~yIqe{9H>0Aitp+FXPXFxj%vmzml-2w5^(epNQn`73TQo6N$Hu9ijSO^+x_&iXTBZ-uZ!_8o+3d#^5o0hYX0Q=9*w$)p#XuDD8Sh6<5AP%pv1+wK;L;-#ZXig!!ZMr;0FFg*l<iH*rJ<d?KpME*>6sYtJm}vfa=AWO3+9lThkn`+m5vX4q32r?n`6D|a(rF$xfI=T<E)l0rlWL(7*unBx=wgK-FphOC8I0(~5|;8+2MER$7;DiB=3Rqw5tqVZw(0Ay0HUR(Qrh<U3nV1eIo$4h?_GJYF)>;K4TxjeF8Z^kI^!+|YB#Nm?XFvqk={k4w`5rQCDU8KH`lAxggcQ<9_Wze<D_eAl3fTDXu?>cBO!|CSq7TA?NYBS9BO2ZBBsRf9Vd?POOuE*3-)J-El9tpOgPHBWki(NP6t4Aq`;`l=!Q)OA}eH*=BIlFsHc2%T+>1o5}8FFo{x9xV0A74Ac62dMXFCDFZjW*x+MlQU{HO)UXRF#qu`L03iSGJLK|EM8vfb5aV-B`;#}sGveX<>p=KOkOWL6Ik**BMy93yC0AE3C1LzbiiQb06UZ1_{JuLCea4X%7Nu3xV%VGynA7)YaRGZP#C}BamW2{>n04rIpLGDM~WhF(`()Hc8Jw;$g0a8)a<nopHSM+JpDO#3npu}A?SA+OU)UiTe=DnpGY8e`DS$&*~C5jb<za@Z0T3tjk*f|O=ZY~%Iis*UGuB1WO;cGF5xAFveD<M|#D+1}2kBuwau|0I!W;2_@OS41QLoZp%8siN1YvTM;FdCkLH!}MrXNgd4?Hxzc^`uEw)~JkJvlV0S*yDqOenAs%aDeQKo?~kd47reGDj6o}?k6>Bt<4AK66nuzgzmHrzM1re@b(zOSZF)Rsx>_tt7gHtm4i0@B=7mvx`dTGI|`mhJebtY0*~-%?d{nqZU0sl;G)iLg&KZXy%&5-)5KW>krX<T<56c`L@%9eV^U@ZCJ2^|VM;2qoJie|aY39&YmRvCe1sxPFg>Z~?FfCWtOlHU^D<n#9U}NH1s2VM-z;Wgi6`s_*6&El%OVc2oeg3Ba-_7u%~`F_T0ETjMS-Y@RDZpMeLD$2VPtDD%CzAmurgKwYa!{9kGmmM)h0_GuhH`EnLj{Z4(ju!K||7`w3McBUzv9?*hB&#^skt%=gr_Y(4GA|?orI%Y;w-z?r@0ntWowAmP!Gzr|ef|*I2|1MY04U4xUglidK1aqTRu0NCDdbr4EYIWcS%gMKZuXBrUs(qDw5WHjtR4BWhpDP^q(a5x|#YH%@}a$F2_dyM#N`#Axd6+bR_m#=cAw6(i5G##A+s(Jf&zte}1%cBW0iSnzmAW@_IfT6R}>LfVnEU`z;PLT8M?2vwp;6z;@>%XZZcek$QXQP0%MR>$8Qj0U`1y4V4}VgcKX-32iQJ;0P9JCxKJ2{*W|9q3nL2H~@?X_((gMb|dtskWPneWz`Al3ZMoaNNMaEAWcT!*Q6)<t%v|JMuX#jDcQpXWZ*f+^fX!)7nrL)1y88I{g-d^q}Gdr@)OklU#j1;OO8nZi9mLtlGMfd7&&nvkNHC3D&`P;zp4elr2Dd*5z<a&>>UIj{BIkfg?H-T*y_SbfjpWop}M9U^fbf{L%;)L|}+SS0(7d*Y6R>u!LAv(Go7OrSzEm>tA}4xB!={_g8(!#;;&N9*yWo?v=*}?1T6Rfh!bOinWW3r_|^xaM|b^I$FP(4y%6@aCBA{s{}Y@_BZqxLna|o*(rSSEP))gXd`K5KVde8`NSB~DFn^ZC9KBZ^Ie^I9!9yW{L`}EIp|e_N=AwnqFR7h$!1PXlO9Q~tPB1(?*Pi~!|B7VuyF<&!$}{8=xpciOQ`!Q$FUSqSbGfXMW*d263+U}^=f60ov&JJXG|6If+e78tFlB;JW$GfkxN~SlVdvCogt`N78dgwaj1dl5gWX>B6AtA>CD2Cn1isomK);}-T`fJ0`|7()T#NLBL6|-Z0b6f%k4@^L8CFW-G20w(P164fG(;*z=3!LRSE(_hXh_k>Gm1`0(~;-5GL^M^Z=+5OXZrVSbGuaF&{sEvrQEFBD+u!K2TFCyZ!-u!(@NNe@Z6I^pypu55rTyH6wHUuGmIAS0J8mlL^WBcWWa2i~C60qhW)ftqmn$T+`Ux^?1@r4|gA~AMPe^y(&+pl^FY)sIICAmxq_k1_gf+J&&eWkl7<dmlA40#~w!vyjlhlgJ3bnLZ?lF-m1F7f~u*!UG#NX<Y-c%l?mCDR;MAF*;5bN^D*W$Ig%8)P`HiazHHl3L;;!1)q&d#BtfbYYNP&qoaa*5C18)yx5yq!a_xtG3gc67kssFeLW*#wxX%W;-;_|mpuhtC&aPOhY(qw4r%4R}<Vf|)8AXHC8&Y?{5wf(QDr|$mvL`z!HOdZ0GK{-!pyNumE<5PBv6hkSEV1n49JnyY$I*1Fim&Kz57nSCDhq=m7=T|W#@V(l%}N*3Esj7zQrI}6%@X7X0<bQSE{_qy$HA`7d;M>Mj8OVoVwuR#hFsJ%?ahAOnQGS<t*qmD<`q-4veM<qC6C#wq<pKos>dH|<Ggr3J+T8A=G9GIn7O715?jM;{6g)o12&$cV|vrCu8b-t;&>8^vm5iFR|WxdgpA~mzK@rFS2Qj*yR36+AUMSHP395J$VD0N7&V@$6}iP-sk_Kny~1FZ%V61zXs?jW&f!$nu@W_hL@OL!BokAW1|>TBcB=^JQ-p=$wGpjKH5%3`pWe(WvuK9Y7L0bfWStjS=~MS6y$eH$_;gjM=XsEf94pUfom_Yeo^BuRN@9|+FR+<4+JS;7qz4ZUrhaU}Stp4HP)Nx81Qg0iGnZ$`aZA}|T&2JbUv}Oy4h@apDFB355^#A&`H?)TV}vg}G|=%2$$z{$15)^5XAnPyfN6g0k{Mnr19H=h1qlj%^OIOBKpo+V#G(2mT1sMY%8;}qyQ76S0X{2~<TQe*0HV$MsE2s@qJ4nU)9f<0-nW&$yLVASn)f(B<^(W`2w}7miVYU<<(K07fji1p0F&rYvv;|#C7>9$Sv_+?v_{;f)>W`^zZ1-7khYm2YM_-p2Lj^lbA2?gw+-stmQ`;_eq$su<)Je^0V6CX%2YB%sqSb%^JLKR7<Vb*;C$7(tmM*~<@6*CZZvHPyp=W5@c``@gVkF0(tqcdzB&#71THSoWM8%xBatpE#o`ynM$|`YE#UteXj0;4up}FJE2}MG(TH=e3!s$6>uuOrqn~bO&P(xWUaS<gCY59K%9CamCP~8pk$`znYBis(!~UsME{q0Mm8`Q{(!&1>Q)h*)*u3s34F>G^S%$G7kgq8l$Qgq?3PMN+=QV5KyT|6|>Cj3T&138BN=MSDbdjWrt)=r{RtM%~Dj{TJEr62EMXZ5n6qQqjc2_%$UkQ6*!&6T=ezXAA371J_IV4m11*nQ~FjNu?A`5tfQwdBF_nGNAE4(M`a_V=GN!t(saeJ+f%HTyM2!)CkJUZ@iB$YRrJx-ATIhl28cj_Bqv>LGwEyF{Rk3n0HyDKyYO9Kg`D#3L9PpVtFpE3fKQX(A$MhO#$Cn|P>lSIcKQ4c{bHAo1RIk0rxVVCAs8EX@i<-WiTp>`>(g+qlD#sMCb^E2nLkF*E^NS3M-(Ok|dkag(+S?lt$22@EdR(g)2JbqPCN^5CBnw&F3eqhK%49uC4)d`S|EGRAL$m{JHDibQsV$dX-R^%;%*3+SVZ#{kzbz|kdNu(oypl2wC10}7E0Rg3E7jjq(FdL>A43)`MI&{D#V7Iq0z`#F~?qjK)Mji?<1NDG2Kb$C;9r$g<%029!!$wF<$GE<ReTFNiGi9t>^%>Rb(Y1~Ws?~S9Y1axqI@YhnyCDyEpc}aY4P^Bb6-Kl(S4SIf;9&cK)`1OC<ibj9;8(Jk%S(@Dfj06t=9Z(rI?H(01|BF9@)+Rbwgvbrgkg~VtL~RXkJqCP^F0TUvl^~*3;>KnuELn?4vwOMNz;xyoc4H9#yYUGFjq9zHdbOE6N#70WjQj0E;Jq9ff@t~;zeOr4~&rk#~c$EL#N^#QjWJ~?nPXH;R$8U)W9?ePk{{`C!Q-MWAZT{qqP26Q^ZkY=*CXDG2wNKR<Tk`dC|31hzwX@3np5G^r4bSTriAf@>O&8_Cu)V7ZrNBQJwY*z4<a*`}AiLmQ}1*UvbkSW|dJ<T>=)r+pN@c#=b)xD|7dHIL2dQ8or%k#a>ZglaSB(FSxD3*6V)KfC$S^ulwbrNZa$NiBwX%if1)a_P`Jv__=|SAC{pIVPK4V$3#~#Zqnfe3tDJAfdl+87*yb~Z3pOAxjiF%b1z)VGQ?rT8SP5sh#4-My0#T-8%OGuWvXLC;n0yI&&~$xC>@s=AV?-Z$#8;82g+|i=F(_PC%Bv?;StgpVyw^_6-SEB6LDvQb5Gj$<AE@WM#vFbBmwAz#S*(P8_~FW32pJ%P{)tpg7p8>{&%^mkrkZ-KJ@0Q`c@FykAv8dG<${4Sz*?kvNU)f7S|d?^2j+E=muup`9R%h+9clswkNzHQ(Xn#9u+ZRGXuNibh_D*nkxCjsM<fjdlz8?kQZPOk9>xaeS?QABTlNH4=~69OSP%sO}7Htqjq9Dji@(1I_g~CzSY{b!&fedGde|EUqP@<BXh=vc%6tNsd{tK7gHn*T8LJZ^NV6=VgeC4+@y^F>dxjg5W>DD`zmIgnXpjl0up`$mU1iDf>c;u=U$3cX-`HZnm+_Mo?Dn+DW|!8`|<JjcMnfTO;^&p(y#PL<xM8LT~LDa3}IAzAV5C=ETtg)#gjN1mx}9WlzCT+BW5mbsKi^mYt80iA`dklvguO=rk{7bI5*lYB8Udaxi?m=ppQV*PM4aqo}6;8=%T{Fj407jw;%bT@iF!F$s-fz{AjilPymadBKe4<Q*>$U9*4y43mw;kY;{h4=q}S;<5Fq1T$h548(_<$$mswvY6hEZh)BD^aI$ijGHD^=)gm24z=9E|0-0<Zlm_jQ7*U`^0UYaq#I0q8Nef=3t+QzQy`X)KSYBY#@T2xxjCo-um6GvboU3z*%(aLSiEH|cPoB9GD!D<Ui>M<S8}UK~gJ_AszTO6ADVC7)n*Z89I2FAw?Rh&}PYM&j7<r`{=y;>s3=Q;Ty2z^ju2%1(ayJH2Y3>xS^8+oQgQVbpAj|6FsGAzHJN`%uvsB6<SVNSo`ZZ!Wv4uA7hQ35r9jMg~*;uRBdPlRVG2krBm$pnaU@&ohUL%`XQ)}#sm26giA7w%FHO<S(-42J0``cNkAD)MhnYNy-x}Hz>qM*QwnGR~*fS@6cXIFM@jJiR-x9?;F``VBfn*Op+x=_Jtx+e+gZ>Hi8@#AE7IV}q)y{h7~*D`ms?$%p62Vy8TQ(n#n7P*SCV45l4;+3_eEbP32P)(IZE5LYVTD#e~V3N~`iX57iycgH@a8M)>Xb9SlB{F1dJCwDB)XgzY>fn?il6)E7ibb6T*(|Q}OWB=EAid?7p04t1MUj1zEf-_UGs|kNN9Rh13>`@B8@-=%ndUW6V9O3IP36EROu{k5HZE8i-}9wd)sKvN2gsHsL4JITmeOF4)IBN#os2M{veg=Pp#ypkeAQp2^v1lyE-HdrQJ&ty$0*kORpvUN9F$*!5V9P4Ln{vc2j1GI+MVk*6sK&TSFzBq+JUM<B3t85ZARcg@u=tSuAXQiehD3f?4$@T-1+3VPNm{QpgF`B$ggTceY=c#%X$z<#$kk84vc40udY$P5SMxbf}7n)s}VtS!!>fjUCLYC_g0FWa@n8<E8>|ErW%d&RTQ{dbXZ}zPg*WZ`5=-`4UC=2UGD)Sc&%kT8Y9sdm?axJ^Sh^z=fit1y+#{xa5GgQ02pp|dsI!vya>%FIg~3o?a8S-O|pQ=)5`~}1&LYD!O;g=#mdj}YgO<G%{}yb{B4Iuw5AfoO286it<1I^7!dr#6T=E;&48z1XM|8AhP?bQ1|Om%(EtD(npj27LwDUJM?qq5D0Ip1#5RwChZVXx8MKvDd_(4-m+O3;1E*CAPTe$%65)J3Yyr^-iXo-L@G;?ZrT|F5KY{_IZHY?(ve~p>sbPBNRvyr<pl%&`msQN{tbv`pGrEqhcdV*4WJwZ-W%D_yLuRm15>{uBC@%X;`Dk>Cn5_gXNuR`Ocwm_KR_5GPSJ0wj{$athjzT6wx2(wSi{`X0%Nu)PgMRp+=O`MaapgDUT?jieakluJ7?_q>ApCyNAB;jp8Wd8e)wri|RUzQvS&o&Zbg<xs#k{q^4AV5c0br0-8l=KyTb(Ybog4;SAQT{?{(30^4m{m}AhND*M)OKal`HkdNu5J{6c|-r(q7N6+!=#*(KP1G*&G&gE2@J+IIjR%)Q2LVb_rF`W@=F{GX_94whuS9erKgY!U>271{<6KhXjG7#sOjjIP`#q!EEw)s4+G>TG>#z1A`Z&(g?5z@7d~u6nz;NhuzgQok*=pE&}s`8_TY566lsoF07CTI4vsJ|AFWOcDfQYX2o*LXBajsUpQskdBn<E1i_u)ZP!}-3MVMEj^Iwo!#FX~9_~I|Kiq}HIq~_HZ)h~j%NDRZG6YapDdR)8+Jk8h0(TrE;VCu>xd;gWuMJ>ML--z6x&})?!C$KD0CQaMDaMI{o_4v~x}}{Bd{7TAGdk9JdKBs<v+=j1b(QDJ@dMxiihu!X0l0{~o0;w|!)TA*WvF0<MJW;3frIP9%dUM0P5qyCopq*TlpGRUz)~<)>KSO-6`musgUWzpny^L@+~<|qR_*{}_uY7d`<C#|FQj1spc_PNBsQ099=Dx6gE=NEl43gRo(re4=(F`($4Ad(@G2%MZC6_5dYOtK>kJ@255gc13MH`lSz!y+@1bN+5N`QEzG)Omdxh1B$1-uxL)4FY;AvMGL_?uT79n&2^kZuwr07JpFc|attOU#na2hs|9N8S3LBv(;PJhscs)1>kh{jOP@uC#z|I$WKho*R_y(=U8Dqd~m3lKASe5$0DiWr<ZH43a}KVA1CDJ+KEbEL{xoD&N<5@$K~4ny0J>bkSZJPdeaP}z9|K=3K%khas3J+hotq)pkPKI7&qeoWE6V8J}iYSo)ySK1ClB~j8bBd1NNiO@?8iXIC!awci$s*cSNHkYKH=;>zFTnhHvdPHgg81FV9nVS;)hPK%=IGnFp$lM}B$p4D~rqU@OoJ_MiodOcHLkL<48pwP1WKeQA&kumwdIiPDeZ!_;+&3s-XTTjbeSm}yOt5A-*0~sIW5YmqgCXp_h7BJep<&%?zRHqiWZukhq{$4uOg`|n1{rvTR{p-<rZ}dQV;@6Gn|Il)0Qd3k`n<aOCP?J!YE5OCowu{I%un6YF~+M6*M0u*yZupkh2DHA<TZV6EvXj1IXjEns(rJOB8MoS4jyM}?s^eMd@({bB=w+c^iO~6GEuvzWdT}?b0G9JZaHyE;-?zs$+}E?M|t(#L!&%kbC`I%bAb1C`&|-#&U^B8kdKYULN|{vQ6o?kyKn>lh*B3BbbS&^=&opS@OYT{?dSKm?|yk4&%@_F@C1IjN}Nk3UUW2wm~B#ztUpDWf5G1vB9wsXF`o!H<Rr*cwP5`NYGJ3U0R>ABaAk%$v)i<*F__z1hFa!=YfBJcvOhw(g~?CBM^+pHu$jOjnAh4?*CTUnK%`0gWzY&JTK33`uT~)So1u+_{Q9^%rY9{xNH<t=&k?n50a1wrgi0R;V$ztktM45gd;~+r_#rBvK=~u}&ZiLL>Q>|GP2-Fmt@G8Du}A{lR8;4}9XC?VnLBWX_w7g^(gW1i^e>kcC57PMPUga%8Y7%#48m1o!Sjn`-6M63YDss$)+fk!EGy?=U<m_72*G=&Ie}1yEdd8(A=U$a4&-t6oD&7q83?%ElkHR8nMrf-EE6_WDN>-*d=c6K3_NADBD0fEGb0A=vWL;`Op-odrhoI@cgrKe*#z?z9F$!bm=-m4>HGEeebp^?Qdb<lm`EYGauaTL%x{BtDcW`c7-XGLS|D>xLYw{7o|YExVdE+Fd3Fn`KTk84*Zg73?7^qs>0d!$$F+!tt}{8c8>B_6V=p9N&Pr7*dueEtIUaZ!_Q`qJCkd)LSkTSIL0hIElS+X>;PcR^HrfKc@r)D*3=XTwIfjl#BxvY<4xY~?vA8Pi3AO=v?Nz8i(%{*6IVp<?b}-HsNEwb|z#$jmEKQU0-CbcLnN8aj6GqZ!O6ANn^J<CXz#TdEp^|LHe%2eq-L-g=kmFe5djVI=cBZ-43BDS;nwrWw&C7c697R{;zGY}74^#({t$i>%9iUTD2fva>U1DFyaXNmHDdr4VJOuAqFGyU2j3<vb`@F@$o$e*?Zq>h=q;<3AF4=KEjmqa1E1oIgQZ=07`Q*b;ipZh;AjyL_ID48KkN$C0greM!iI6t4i9uJ)mUV@31L1ZXRW8D9KD<6hS8tl|;^y}5qel>#%BIo)w~lQv*|N%NC_;u4Y(q0j^6f?W2NN)(<&8?0kzxLyi&s?GMC%|ee4j>~21GEL9PV<VDo^})t$s)8gLsDs1y(PcvIZET(Zp~}pntqw-X_tHUq+pam`MXak)|UUkgHxWp0*?XXI4F9@(<J^2fAhYVJErfPU}<k>(BoOo16ay')).decode("utf-8"))

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
    try:
        if isinstance(value, dict):
            return value.get(key, default)
        
        # Kaggle Observation objects have attributes
        if hasattr(value, key):
            val = getattr(value, key)
            if val is not None:
                return val
        
        # Fallback for weird proxy objects
        if hasattr(value, 'get'):
            val = value.get(key)
            if val is not None:
                return val
                
    except Exception as e:
        import traceback; traceback.print_exc()
        raise e # FAIL LOUDLY
        pass
        
    return default

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
    except Exception as e:
        import traceback; traceback.print_exc()
        raise e # FAIL LOUDLY
        farm = _farm(obs, _seat(obs))
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }
