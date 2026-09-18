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
    'c%0RpPp=)vjm5u8pmi3JW!cW`Wa(urM79k5iI6b_!@y)Pz#y~m%x;kHK9Zi^?e6Lyc@9~1Wo6}S-FLgISS%KKc*y$c|L*<AFTei%Z@=FAm*4$#@5e_kU*3EB``_LB&tLxg-~Z?RKfV8-zyI><fBo%$-~ZoF_r87o*PnlU@%+i_$FJ_a`|8biH;>+bxc}w5Km6(5cTZp3+%rDCf6AjDo__!6+53k)e*WhDBjB5t-`(8&`0m4(m+xNQ+&p>z&G$FYp8xRf!^6`zcSCx(d*|DK{Qh^xi9UV&=hr_TU%pNHr+aU1UcR~=>h|gJqr2g6zdjD|R(zw#Ufw)=wjbCZ!^u1dC-X%%h07ugllbBJi&x*>j(GR+ZjI>)@ib1azmrSlh2Oq@`s~Ti@BaVQ>x(Fzcb$G$n&q=ck8k#Cb>DyS<+rRQ@4o)w)wY1+7&e9Z)BEN0UwilG2aSC6>gGlAik)^kuekg3K$4f4-D<}0hLfC?7*A$}->{qGywcDNcQ3$wJ)<fx$L$@tJd5f<Gkf{`_1%)76c?xmY5Q)5mshROj{O`!bXU@j&FF8hzn*ru@?4-Dwm6GwLettFfl?f2*ippGaCcgt{9|Wr_Q%I*mFCs2A-Lu0cbUY^qiLnf=R-1FdU6TTO~2vzgV3vtm9@P-pYn&d!~g7t8k=hM!{^VQ-8_Ev^Pg^Byn6cV>A&4726#N;IppeEvO-mbL5as)4%GV4<IOTHyT(K=miY=x`SIBeCG>vTmt@x{EPdmrAL?~~sF8}huzRO6M^NAlNdU0%wP)oQ_)R;P<2sLs!JA9~_dCeL=Hz*1iUQsUoxmrC!~e=#zcYw1ZICt(YW9@b`8A!Bf`{r3D?5B92ewJbIs-1Q-He1#%7K9TqdG;B_D-}0ybt!<W86u<FS#MCo0ujpZnQAgfCWs_wz3Q2@fBfqAe#k;M>7ssZ~%|6_x;m1FJHZQ^yb@}7cc($0WbetPS$cjNU%$P_c%lL=U+J9$4~3e`NENGo$FUU;#Zya7r<nv?hWS$G{p@`2P|d!z0!@yPfTkbJHs5wZ&9#`c$4*P41se8WX18Srv$l*mhf<)IXi)Y_q0;sru1TbHTEPy)_L;D11mUV<SuP?eoSsPjM464Bc$3H+qPpyw7KK^To2hTIxUi3U`NRLE-#TA=1$ou$2L80{U=YIygB}Hb}@UAxc$O@n5U10s$d0a<7|eeo;=3)A5`|yi@($|fQ)I-a>S|4)+_X(T$B;M1|L^UlA^^ufdri)-x+JU_dd&YErAM$8C2!8`*8#}5Z|RHu^fz;*t|JJu^rg;MXrP!xXj(9&m-c+vWi3cMQ)D!*y%{H{Ko6MSRwkekwTeDx{&%g8-AU=uP;Uw(*9W+VPO}^3x(4#+j3o31*n+^rp|$ubA@qm<4vi9C7zcuU&+6+R#nhiCnQbkSCF(9OxxT&PsZfq><;ej_`CfywPQ}tRZlByix9V2%2nx{nF;ISDB<=<4d`!@I$<Cov!`zxzY(LZJuLT}cFR^00TeI@2c)u&>-?T7*mdovO*&6DKJ_59r&X6B2!;5SpW4BhRg^;n)I#p6WSa^WCXx};coY?Y1eu|+=;=NXsY=d5)e{luWR;<$mm$Ir`s@nw?<U+Z%vrUQZ8kWWZ3>mmucWP3`+ZecjUE^2g!RBDFP{Gxt3>XW?l$1_=kNb}TXcx0$5wUt?#O)trv=T7;2|Ce1?XRRhtu}QMH5l<*>!lnJ#bUF;!Dy{Zufk^Jx3R4c$Au59_?W@VO3YfsqAV?)rxl+6BCZt$Nlu~Jj;Eq%BOgX_}+8{V!D09gF&Bn@pvg&7;k$R`MHw&a0Z-fqmSOAFOLODP)y=Za*A9$t?|)Zfl2U<hhW6tYba8-dl=fYHmfPsK#;1ii5Ou;^P}^pgHMwFK@DRnuE9A{epl#qG}I7|GPYng70f<~goBO(Q~K9gL6J7atZzlD<_YVRbd@9nhkjP{Nod7L*TJC+)O%{{A@h$FnjBg3{MXRN5_H=1u|%j;(Vjfk5TpR(beP<IWIsojHq@Gc1!KnGZUrQIXTvIqP9J?=MvZ}UhwIk__Z5z4Q?4gZ|1}y~V+1(UybVaQ6ub3nj76P8>iZRMc0WPqg-KngkD*#r)`acH5Hb#Xy5VCZ5zrte>=?aKM=5}G>T$~`qeJ9qhJY&A%7Wlz)I~+)cOOoLO{gZqP8qgV5q~_uiFy~ajC6SRCNXf_rVD{{{V2s}nIA_3G+4+TLyl{8Q7fggZEYbJdV7C-z=;9*WEwioPtI85ZKMtR40s@qa(%8#I7bIPj^8`4l}jADk>?HIY959q=uGckzO4-e`<{Y{3=lbP%tq)q4dUg2r>5<7zYGmb#;}pnes&YN#MA{g5S*Qa0-cM>XjWRm%y%CAq<O*{89D~&?6o@k6mV$Toy+L82$(J4+2nav+NaC4G%j$nU)pF2cb6kp6D)wRy;$b{AKvOf#rd>=a4*72<jvnr>ieh9{>*~ugi2owcB&F7)vDp08RQ<05tGbhzH&;6iZ>=Aj|zE(he7&ug>C}q@EEa&e;z4w4;(GmE9N0j5Uy+rQ&67d7gt}ceF6!G!lGg(YJnzg3axc#qI5p%?~uKnJWg*Ih2)cRo0d@c@O|X14l0{!#B??ea{_tjz9RX?UNQPLMr7@o5e#%#A&kI25nM+xIZH(USZJWp#>AQX7zBkYf<5xi4lfaL;bZ}1z2tJYF|^%WP;B8kx5ePbZK<KRW4xA&6eC}c>3NUJGm`wi`S9?K8v8**KTU|^${?1@IJs>Y9Kn6noD|(;@^v=dek6tLmTD+P33<$Bi9cLXxia<=^j~I-Uy;pL6aypv2_6lSOw_0f6Id05X-hYj(}jm<R+?~?*^$ph2-rkSNn*&;mIX;Prbn)-)FoUkyp6+OH<7L_hPRtB5NHT1o(zsvL{y8DznqJcSustAC%E?}znH0#IGCzQ;wEbCJ%?quECIE`qlCnylg|CeAs&MS*dG2ODmGm;K0hl(ka~l#W2Z+fdYaY-&SM}K77U8u{{r-W^tC=h?;$g0b7C!4&33b%7sTQPIR=L}&EJl{3%^iV;{1{&i@562jRfRjrKRFiC&9$xADwk|YL6s>>lil0DcHW>b`l~mYMSRg^HsVh&X-Ca*8VCxLtt|CouT~bmLw;XKC*mLiIo$FCSbI}(ufj3<Q^EP$YkG$DjrNvB9JaRqZV*lbHyo0#yB|^l%MXVbWIlqHEuIEh`1QD$k7|Tw$4r9Zzim$utJ<P&;T7z!6)(XzET=1kb{JdCg#zGP>h^ea5{Pn5~yDelg?aRw(25`uCg{rC2I<)mm#h5pLl}T!9vrbWfu%32U8$~ti}Kb<j^P2WC{n2N33ZwxsLE)1<=_V>q7L>aS~Iz5#T6EDW|gVDOPzc0!*aweawz=ZJ!L26?29oTiE6`QjCC@0HL~q*s4-qLcq-#ns|b0y>7EWk~-^-UQ7A{puS?%ioWCEFL@3?w8x@FQ<Cm*eI#(2_vw}pIj2?uEh5iOU_7)9RcfW2WubBHL!-MQS>fg@;ro2ni)}OAV*@iWm_7zIO(E6oDiFDnaSy7~PU|z4RDFsKB;{d<&7SO7FqJsSQ)(C?RojL%BiWe%<ZRf)AjwBa?*AD+r56$E(YE`5T_<jvlUn^<F5Bx$V(L=NX2djF`hV((Urok{_{ZM6VI2u3a)Z9Qm4JWy+k@NkMfT;s_tGc>LIp$?@+799jW8C1C@@{IzKiYiJEbfp(R*%S71o8SxKT0ERdEa!MujL|Az!uQI(-vTErcWg|MJVj*)9efY#v6A^R6>q-zoms*+<3OnF79ePU5UqmC(M*YoW22!tE9?3bRVOpK6*M$`J<?6Hv!9A*venGRp8qYo8$~BHNDi)fXk3Lkd`^rpRh5^fua37`g=vjbI}RaO5NQ4jIhWJ+-*+EcIZC$94L#%VTuop@3R~j%a?xs+A3~OpOPdP7wIE?}tOI7(?@&$?jPetvxwm9to>6+@QiqkivvbZd7EE5<<&0gw0C@a@#|P#qaMaf>9Cn;bjCiS#qyUtOSB$R=uwpBkQ!rz|P!zDna)Q)CV;aHBU65xY*m<==PrmKp5w9F3$Q~J5dzb0ag$AVi#@Eq^<ICLE)3n2q+Zy#6^17Ntl+~T_kRv-=yD7mQIiWa+ZB)R&EPG%T$&MgOxW@QKWl|5f3_7V6qCNz9L{Kjd|(i1V&(;=P(Kh-pWdp)4ps<mhkE=eTM<71`4WGx+>5Rp<;hvh4g=t)D<U#ik$GtMP_(s2=utT>ZCsaOmRwxu%CD*thFN}jQB-{JN~z;2q|Ez(EhF&;WF(J-JKw*F#|=oqu7U+X))~fk7;Mf`h72+y>Il|khu+`P;|b(q?3)-|8}iRy8HfSw5f>jgdotrS-l1=e{FomCu*;l;|pq{`G5v7Ox|f0rpnhg3Q1GtmdhZng-Tz5A%m_XmdTm9QzE{HKJs>2{VuL`qZtiaz;2~*7z6n~npf`X^tMcL*f+Hflbminmj?GT3D@|8#?Cv?Ybn!yR9r<msm2dtJBjS9%FQoN9Mh(8$h4R!n)hODh&@aJ9n(@Ix?*uj)!${>YMvj$$W`?RXa^~BOPY@VI`Qy`(B~Izr;7ZlLdAg->3Vr4e{^7P(O#AIZcvGE*f`V2buT)OZYfw(2tlUVZk&qRM%Hu1SVR&zX}UkXmXw`>h?kl4l`TROJ5ki9q?n_@2FC0s`|dnK)ltS4<!%&oBY<M?r-S?$p4~qp9%|^HHS1dx%Nx<JZR++i`-l>KGfbhA@U<!9<m2}#<Cwh)3F1Pd;zkI7h)6nkxiCEbz8%J^oNySlcf#Q*_BTgVlB6E}ZSBx_cu@O;(hwF_X?LF&dC7eCikdU~TyB^5PP<!$&14+X1|L)_OMidS>PO8k6%+U32`$`eY3ugTKPx0lr%1GU)%a0i1AiO-SqxB6yaf?fHn~7Pa2YKUEid!Ds>*sda+m@)<}PT33mb!eGV_@vO}8g)jC#bC*HP~VCB*`1;L7l+JQ@yC+d=_(pPxtACju_k7zosA*F{A7ts?Xni;v~?;@Pyb1?0Bi-buAJN=-HFHWinUq~CdL_i<A=n_O=tXmirKo5@+xn9j{qm!Ra}xK#oAOb?*(S>kR8zD+#;w1C>tp-<0ziZ5U<+$ysoXPpM?^@eUigg!?7LnIdMD4nc+=ptT`(4oVwaDNOqqHa6WBlB9BYcs)~Q*}LvqdlRi)FHp8m2nr-P?*1iy;ZXE!OYru`9t^<rYeQw;77H><2)2MP|g574{xif2H^b!Kj!W+t_+-HQ6FF7a4zWKf}-{r0jMiR)K!2+R#c<tyo;a|D03hh;(F?q!x&+c^9r>f(%HlI6XcIlAWB6#n4G=I_J;&LRJRk}RKhS$Emvf&boq<KH&ls)sckApp00?XL<H%G_|%EC+iOgaSHUcxQAjpGDl9(f#GEi05Q!L1z7hpP(a#F3o4`E>P(aO5*aA)1V5lv$cQG}b%$-qfikl2I%&2`Zm@}xdeD&x|Zh|fstn^AST7`%toXy&>mrB$$qWY5@IFO2{pn@XoV3PU3B^bo)E%?KD60{hitHHrC+`k0}#u|Kx+650IJ*cR(VgaqrCv}Vk3Z=UB{AOQ^kyH7!;CkH8y6B{H&FvA`3+Xw_Z)RYlzM%NTC_@ozysVo-KD<gx1E_?sO*{5m(1BN(e%X&{Nuq+9nbR1=P(??Dz<;S+_nM@nqV?`#>8`ex8bz@Bh>Y2U_W@3#;-ZZy#!;?*?7l*C$>lM!^W9Dg+l`do6zvqRrSXOPJSG|hxaO%qDD)D&l)=X#^6aB!uNBEGk)a4Z^3DpC7HSn;^hc^2=?Na8@Yj#IFQ8Roq>HaN))~*SV6v4!!xgdK@3f~n60V}7^r^OSDq^hiu?*^_XiK<{o@WpWgC&ionO3vXiuBGdnx)Q$f8nC9LY(bf5jvWJicHbfAbWRlDem1f2B_m=CEbImFps`wuCc>@jhj6rKeAAUuN^4CGoE9i$!}OwvzEWJvOva*)$;-w^x{%pO%h3q{S|Qc=Q)ESoGMd7>_&Mddp|kKQtXuKJIYpAciBXH>G0d3A5KlztvLA(bh+lshw}|lqQ)2Mh$oV{mD^3CVitiXaF96;xv_~AlPfqsqp}X&f?+x=tCZ^~mQV#RkqK#7g0)**z)P7k72B>tHAd0{c!GXrY~yItSgF|4e(IYhL0grD8LBwU<UELNE{Zr%qq$>xI+=uJ+m~?jx|7ggm7pw(iPa~QiN(z?hwuuNc1zh`1G`pE-7Qk#DoP^3n0^48<D*FiXcM8M+6^DWD4{F1xC5ZZ?p7VM9U@tOjADU1q*~=VFf&1SWaSIO?d2i1FAXXH&OE1f>=+MutVWC$cde3~fZ#zTrCiZan5<&n9ojg)2$=}ff?B53K8f96rMSmud~)38x2d~Y$h$~eXU>#V3EP-f9EBxP!{%1p3A0a1j=JnmPZOR}xoT03GeNpY)fOS45?9+E_%({5bgu}}&Q2eD=yc^j6Z5jUC8d^-ygHYA<`v!|yHCtUYe5BjQ~*_~>dISIaGZUSjJs^2qA-YS@~Wv2L=Hovq^Cr*a#v_jDhVukhZtF*0umB)!a92$gAURyCFXgjs^Y11la(8H3b&R#{V2gpNy^MHhW7xR?i7RDNpW7vMj7^yrm2e9b{{WB;W`a;8JRjr+pj!SwVrwDrCdEIaSwVL)EAeOR`?{c4;IKW)2C?KNd+^-a@}(q4~E=mvht>FyG->pZxo9N!$+Be?J>^20syGj@K|KwhUJzXm0U7aTc#OpGcKi0P*2bh(d&=J)^=6YO66F8aKJ_8LjZmYGfr~7ghOGQkAw{^49Voe#7>0dLGzXm3$pOw=+pX)khf_BlG?rF*QXgZrXfH^@!op5)L3Qa*=D+iQzClI()z>Oy^C__ja$dmxZ*-%ZWFgu%~fWtY0~s1tjA|~d60w*B`RqCR_wb<Qd$E|K8H+vU8P><z=rDes_r)xU}ptXwAiUY{4C)ec^JLhuQ|e@GvrbTGtOUhF4anajU2wl4}@Fd_81PA{pQ*8A3m7+a_i56L)fFU`OcX~Zg30v=w-B1gU+VvVjQ2s(O9(HnF-iSX%bj;(+ES)&>>$)x$NgSn25HbM;iX)j;RmgM2*QE!8;Ye_?*xO5wSU7>o6w{vhe%Srd1m@R*^#QU{6llfL9%0HRGbOAR4<_Ob!){ELEXnk7_e**Zy5J)W)whvXVz-I5nlZA^x(Y@GixUJ0>Tn|8cZb^8Ul}Doa<5k`Q0ZZ1*roM37(#m0IyE&jXWG$ryW=#oaoU&huNR$^~k0@TbCy8-^PBl4XrGS#gy36i0Nx-=fr$%$Vu8_N*gf8L<<A+If{L8iWH8MkG{oX#oX!pT1~i@-AD2l)@f}-`)2<<Q?70RHR{|0|7dQcFiC}$cleO6bCZl2YHQWJv84E6HcpCk7Ezwt>6hqWk}1R$FN7A3;W3*FO(v?)4G|CA>VIU?zd>)I`-oP603;Lv#6_=BC6ElK7Rh@LX_mA_0!x{ce-?B_!Mc#z%_6^vuIKhQ(R2O9H+IaGn4d^jP^lQdZsY`IXYwbfU0y^P#a8=!}<1!tF&|qW)|3U)H)|m`hk@s7Dn-nNUTNyfz{tTUd@CNDCQGvdFij!>QUw60<>raT3Z=~2psK{Qe=Q@ojnL-jXU0_6W;yhg?lHWmxP*k-EEJm;5c%Tf9vnAnN$#-0J=j&&Z#C|d8CDo`JxEv+t*K@J^A^a5BBPHN)0SjK<1M|4K3O&3>Mx!<MGYts6|>~r0#N9`?59@WwduMW80OV%n=_zgVy=-m?a8)^Hk?{==-tVQ*Z>If&5V(ozrCGJfEVG2p*ON3#Kqd;{cV7q;xV2(W}d*862{6nMkrC9Pu8RNq5UcJOwyw1C@crlZb>kZmfG>Z5@O?N9_|U)Qm_ax3w>n#T$&n>Ey0v<*L{~L=@=C!>4u=JPnGzk>^%kgR%jVG@16msj*zCx=aF&Im0v0eUDv5_nYNlJ7~xBaJL7yR_F?a#xDExnxx0;-Yc12@Hkx-UB+!1r)Gt4XI0u{U|M6lih^9h2+-r=jKETwjsU?(`wcpvh~THVfLw;vW)LY*RitGOn+p1#<W<v(AL1Y+j7QcGUh?!z+*bw%qEVfTWle2Q?luc4<S6a#)>=+&L6%?Xb_V3G#}2fqAZFkFxN0z}l9OJTUXK&{Ar{0(oMnDG7yIZocE;si{Tqe10wn6!vI*srj=uyCyj_n%Gu5zE?kZOOq#x07aWSrL{joe>W$;MwM!Dqdqt!E-GuHAO5&kkWR+}mo9jW>45q@Ca*;wMFl4n*Pwt51r*!C#QtX$lSb%hOqf|803WO49*92fna<=E!BSm;g0cmR3tr+@6Iq1(@03@Z+qBLjH{x)IXdY=l3@(b+yNfDl&QXxA?djXN|hhZr7?dQpWKg6DoUY{@*9uxc&D7Fl+0p70~{fAhf$U=6l2<cMcvO)wN1R6#&YcF!lhpid(n>Td}^QAXN@5e&2#&qM`-@SmO&=HZkA$OMS1HUTAotUUL>;#dnReKEj3v*W=)mpLs_2&j6w2~Z}?epd(|pQg0XDBz8lE@E2I-W@gmC^}UNY%-Q}7Cw(s2eeuFhf3axjBGiINAgJyeGrXCB!yKW2>v6eiMOSzFiH$gl&VEkRbBz#G^2+Kavy9Xinj|l#~i;eaCB^X8Z8~4jTh+^*j=K+NAyBnWMyz2Bke@fTDely$j`YoiK5YlxerU%K9KR5=pLbrxnYBbp6+HIDyQS9GIQRDOgy6J=Z0p|u2wS<B2{EpRjOET$_%AjR6)Y~LiOmVG4xMsuG;|xx~0!7IhHwE7&OizIz|ZZ0_JKJghLl7v@RRx91u#En~qZvj?<~5Nz2%}9vk*gDRBd7iunEMFU7<VBG0=d<n$pN746;}OcZQ|Bg4~*F~>*!hBzt-CjPh1z^BR?El~8qcpy|O9LWvA7(Ore>$H&&9$S1)s9#p;LY?}<AmXr_7e|k}UIC(iohbi4@lVuf+Zasb*z3$7N4$RPIdu}{x-EP;?K(sNib5iCJ#swzVB;1LQ(5&P@sa{Z4i25XV1m5x*wh%kDV1m2*~(g}Db^s2EC1xc&*L(<oe|`wM;}wPi3-jEGq{X2>MlzREv{&z#~sm}p2!u@jpt=X@14X5?^027Q)KW~tMF_tCV!+|;j~2W?dAeMGsDcCg4!SmNeh@dn;T3l$Cn!Q+SQk-E084wi;(9;cud)VJdEtM<I4*fPDbfi7jxLtbnP)k$RP}Fq<Azy!zSa@K{1-<*uUJ`{;H3GU};!&>7%7<SSg(YLd%M<bq&Cdq@CSHMBRc&ke5xotucL4ICOQ$KsrGbI#|wpE9X=hWb?)S8KRjSAxd&Ka(qkRK<*qwYY$<Mh-$2<bbW@|fa?}R;os&O()XWC@VP^iJ5|hO_)o-%d!Wvx@i6NmK{o%UM|V@a@#1K0R*WXH6^5Jm`D(l?I=Kk8THn7{aD<zoN$G0Lx+|19DNr(ZKpW~WWmqcGmdij#)#{5s;lvS@da1Kz%%GJRe0Vrpj<#?auz}|^9@zzUi9`i#wBwky`I;qC%b-?RJC)t4*oKS%C6W?K-m2y!{stdKIv-vpyP?aN?@I%uayc@VJDgY<Tf+iWTJ1D(kEl)`E#pX$>z5YuRPJ{5Aqf#$E@3}O(BFW!<;o;u-aX1QfppDjngUUbR>NUZ;CG{5O^`lVmk}sMEs?(m#4eKmP=GVZs#8cVnq?>Z!|L1H{`*rlu9^z$T;9vzxOf6baw`sG8cb;8taTHtGjZN1YHVJ#9w_Q<lbd*X3pbzUKo4#@BcjPsAp-!-g>gZoz3Uga8Z|FN7GRflq6^DuUL)ZSbLP`Xyc2s%)2dGX{9NNJ3oFj6QLkU2x)57i-{tDmlU<l;8xabW8_;q>B1*g}fv;8SCn`04R{OVB_bh)oHg>rKY5kV%v<f_Xafa3=Xgbl?ZNp`+Cws6<xL@dRh`397E_0EA!XR^pQZg(YHig0)&qtPdE2bJJ0ou{nbJ!!NzqeRZ9|ps&=5N#b3#b~nsl1BFaEWi(hwe>@B|6*=jgzLvX6t5<qu6@_Qk1x*-zrL@>=PqCoTS0cgz_3}Wq;XXOh8d;3F!bGJMuY3Emovx3lu4b>QJeklrrL{Rqbs0dOK*GU!dk>u3&MQD%MU2822AW_&%i{RgqN5`my27F^g`EoB~-i$q!AMiifI69r7A-@LN}k2_|;PDQgp61>S93_`{{NxNu+$sR*h#a38%-6V|vmJDee`O^i(OF&SXGo%_*Jzd6B!%h_lMbDjP%nolQq7LjCiXh*TQ(9cARwvWf@F_{gS|Ieb|dj|l+IelFnwXQ!D{d;z&mZqg;e;k!1J{W%Kh2)iLLz+ylq5AowXJX7&*ahZWJEJN(XDE9wLsCg^!b2e%mF`64jT^nX%AF+AGZn>_Q(7(gC<Nj}hyK*X^?mdy;ej9j&AG|YUA1*ZJVx&_6|wo?-u4JFZc(cysizgfUK-(xaUxMclS#?RV1eT9TcEX32oNPWD=_s0*1b-zG2W6&o7b4;Ma^%66Z0cP*uY0*A-gJNR_q=DZYpkzK75RV_4d_GqTRUAARN2qJr&rHfnBK^8Ol%#mNE9**?d@Pvl2frQjesJhGL4GU*&2AnNEGfCV5_BT1fzA)eSj$B|&q+VlBMY5)`wcR3g%+urD7h`*&8(jLc<T*5_0m=MdSx6Bv7&K5OB4OX=MiU|teQgUjo`s0~uSUS0+z7r8sSJWXMb4vIf#?$f(O`(MRdy@RzZZHK>tSTyB6DJFt(J8*`c+)p2}qSQf0!%?VW2Fzl3C1K|St$`zgyDf%I1VW_?5*R5J%G9{mW`pR+h1A%L;*{l%Y(v_GYMokPq{~=dr6K6>DB?i&y%-p#_;mjxBf4;lDm#*Mu^&}Q)(pSHQ}V9AR(M9*Nmkp&Hlea&MjWGW74#_!n9>gVyaHL&wQp`ZHY_;~$0(Zf_CJDOjK`JAjGUJHUiMj@yg}i*Ft;en0*n~?n$?amid;n-&g%SIg&0L%IU{%^ija4~@p`S8*M)2jH?alPVL$`5+Xh`qs6qovcTz!ICMsoAp8v=PgLtwK{g!j}3LOt>WOy%}68}Pbb79VWN_qfVa->>YvtA|tln0&TC$-4{8_s3g9Y|%E#<{BI_3((|EM#HOr}otZB7qSf4deXfh$^VLI67%mNq0uIwz<P8(EuUV{=lL#Sm6Oz{LuJBDsKq4gjl3LoQBu=@qO&2my{QP(^R3*C^<@XQB;U?x&%&h)vUwtlX<u4DS0U#cgzOKv{-E;$ORp<P}xz6!kzDso^6PPsM3h>geEA*4UmW5X5g&?#AuAvqF-5?$~vyZ2*oxRm395TrgL(|J!EsCNp99c%<Lco<kfOjzssM{P*&bI^g;yz#NrpjLP$sXL8{7u(#qvbAF<gBqm_&?0~O<P>JO8PMz0$Ds~I4JA#YZTKRNw68t``D?>(+dQqEn3d|*4U1-?Z}+^Il9>C50VCIvxvZ&m?yo?_4MCfesqt%&+TIiz+2>HHVtB3X*ftq6hZpsFC={^RZc1J3TLga')).decode("utf-8"))

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
