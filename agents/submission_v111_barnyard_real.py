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
    'c%1EBOK+UXk^CzIp64*6B+u;LXo<E6b3}opR`3pl!2s)p0mFNk-P^+d-J+V^{XHTxA|KV=l;@;R&3<H7WmRQHMrQr=|7ZXG%dda`%dcnu{>@Kk?=SD~&pv(o&Dmdn`Jey#-^Z68|MT}>e*N2D{_pXBKb^h3zPoyShyL{Y4}bpo^4;~1mp5mhzw7nw$It&<fWO?oy}Eio``i81)tkq^e0+O#`SAJS`_*55yt=u4_xa&`|DpGHw{JeYewcpl)u&JY`1YH*qSvqg^x^&VXU}J9|8(~8>i%J)z`NVKhqs%@{fo<|<v876-P}xNIQL}OziBSR{vGpSyS{nz^XI90_^=&gT`psYfOy+)!U9c)&HMe*2>BvxKltL1qq6#$scaKVfkv}>aW2Q&LT)Z!U+qVG@oPY1EWrAa{O%uS3vW3ATcI9p^2?Wge&yZ6emR=2h2?mCxgO({Y@f&S^5N=k^|+H@^3J7HZ2VW-;a;YhI#-wXrYwoyn0zxD$NjJEpYCrz2m^|K3@x0!68m2mG@fg78aJ-Mc92$3fX!3MU?w_{8EzO?wE0c<pN{c-GCI{dCU#mHQQu<G7SKDi>uq`DAd5zeUh|K=y!DbH&hJIr*QTORUbBC;^jmN^_kUgfeoe254&Wy?PvKu+A0VD4`S{MF<xe;cMEJ;OAGp1_xqAKZ^B=D69<Fb$|8q0C19dyJgli|5d|<c5{-)C5REn?3-#*arfqfV`nYVAhdHKmhBcc$&_DwGryZY+PkMA|{FL7hDmI#Y|NhDlmt196mjUUCZNN5!MAcp~Ch=7%#vk122gdpxbOkxE|BsdL3qTY#^#H)(Ha2ldR2qz*63><Pjpt!Gh8m5Mm_Ssh;Naj1P7Wl=H<fz9m;bS*_o@TcHzN0gLUXC>AihohxhpU_K(4()o&!$c}<u{cbHNA}<z?n!4sdm(OjzeWkrOok3R+@x${uMqLK3M#xjxbKm7_Rfv$zTNn$PI^C@h7z4Q26H2(N0D=GBX~YUq4IjY|z`wyZ^`@x2t%`$}~Mm#(pB<XQu{?gh7*ES!L$($G4r*=$K_>m%FL0&NI$1DM_L7jN=`$1Af3t1p{gZN??Pn`*X9YoqY5B_3V73nf3GXnkSatYCF=J`;ZjT8Pw$=C)=EbQu>Mg6S9G(ueKAE;U8EY%u5#5#jA}0DP9=zfh3+=U*O*miWPU^<$#_@*nd<+<jwUT2gg&fCEOhUH$bZ525mceBS%*g4h`x?;LMmJsVW298pcM3_Y`94XY@hqJQBkHuOegH5tAP@`VL2T-tlxw30ptZIKhN%G{@JIv7NZNh3v7M_ss+4etb6~3(<ynXiGu^H<HuY869`e=K)-x74bZAA~K1OoVopYd;9qB`FEd4!1p+=pZ)DO)3eul@{7H;!Q%bH-Q~yMU)|mP`B8v>+x;EP-bKX2T13szlUoJ6f>sTl2QKA8cr$`S&{Jqv1H%Z<<+UQVpn!&t<ct<Q#oQ$m?1n`gQCTE!i;hZ0l=gVpF0#>wZx?n?7I5Ief))qL8?YF1xm)-kbuA9od!<GP&VOOneIFL)V`##LoO`3K63ge7cABGJG*;xI`L%}=;Zb4KQj7|qjv<uG^)^gKF_UDA*g!lLYM*qu$?hX8^5G0l^#R;iSiObMASaVvi)*ly#`K#*sH`aS4;{H;m|RyR$CEFK6a+o&b&TIY4kO9&Ce0DZlr*mCDn{#;Z608*Nd$@NAz8}2g$8X$R{rD(Z}C6dE-Ng(G$!~YxNP$$6k4C}{vw9XFud~vz?UmqQ~O!q4Ds)@J|7c<Uxd!fmLshJCaSiE)w8t@8_3~6{#zidiP(YQIT)vQ53`UEfaqS_5ZBG<8tX^|_Kr#WlEA7^Ea6g!^2c4oPuxF|a7N3#Z!J0I5E?YCmUI(tXy6tnNmD$tr;yJpniZWy)uI3+F|l0r{vuJb#`cp&3IXpEVP8j#@A<AI4It8q@lb=@N14z(-}z##C)nx&p1;#nBQt9BYzY2{kpM%KY|{x&j~sEX8-}a(7j%#J$LpIvoozeztvbEUU!Hl#zx$N)juR;wyW8G8_u;gI3cACK(b;?NwqL*IS2`X)IQ!87j9hEe+s`=u(Y;CDcRjf>B7h%ecz?j_Z$nBa?wRFSh(zrcSz++P;{_-8CBzV;2pe)gL9cR$*dAJhbAJ(pei+B;8zgx_giNmDy2AsE^jn13{6vU`@F^0*)U2t)Q{E2<4CQb~#bAhwMr884A%k%Qs;TdDE96qopz^N$FMoK{%!9I{g>03`i8LJXmw<*|XC#<>3EEEgKm4US0q(GwpWT12W%o!1*sZbG9FUhk1#%Ds-a&hdMI6vP4)Uwz*ykuex;(}fY`z~h)4T|{HXX9-LDl}Llv$X@IK&lHo~$8xin8`3##$Hpbgy}YG+D7`HXu_+CshGv?CN4%mJo^*JqJQGkK4Aio6ht}z>ijw9r(TMWH5`g>~F?(>b6h~F18>28UtsErnaM3Kc6tx$vG>d^1cGRx_C4<k8p|nfM%kJziD^kT#;ZFNl(M3>NLO*94=1-y{8+7xi+ig?K9?#0E8NLZb^=@9{=zo+0n$-)2$OWF2nxe;-;~zeK|!*8MRme`4@Oz2wtSg?D~D^_8OAN#KZgM?)JScw0|GP#P^*$tJUF;@H)X_K@l*Sok3IL6OG(}Z9g&lr}b>I3AuO~pO6>5iV$F6qg~RlUNlU|WaBL<qSb#zN1kC%agq1t<V)N<^hV-a%yz3!-NQcyhSBAXj&dMnu5Q_CEoKD0X&lw1ex0z>b_f)_W>#c+flMh)hNVyzeuGpUX}U8$*yEp<Gm6Fe9uWgJT%hO9?*v@GzJ$2u?@x@5&BOP}Y4zd@i6*=>76$cQ*xFNo4JGqj(j3uVB`Bl2uxOPbr|`+ytJ9!D19Nbzqg`6}(v1;HqAD}3bFugH4{tzAPPI^06R5Wl4Izp_Y6NaK2^uLdV#Q{?)Mdo}Ml=GsOfzV`4u~jD=gZD@ZM`mE`{#j$syQdtLa+vdU|!+fjRL16jiB<0h*~PG$)*1J{SqkGF5;j->PY#D6mgaNlgwsRsNpPGG|V1^_J!8-Uf?xh>^?%2W4pc2kt*ZEu;?AY0TA#Y+_In}v;5i2y2sxPSulj6A}r}{Q_ri7uZ&$CUX%SU&eX{nZAT#k(k_fugmy81EnwKAqhn}pl6-Y*W_lo{6D!o$ny0c_*<dU8p+^hBK%J2*snoLQW+OCW7wy!zXW>B;%a~v<=zL@bpoWA&Ky?nTC5o?RSm=f?i3+XM)DJux3~601P#Cz00v5irKMC{eoVjpF;tIq`J840|EEfU<Dsir{K{cVuOEWC?pIn_)Hcq!7D~hHO*?dzp3bRyNmN<2-h*f~-7PHKbdltZ0(xUnv)MxV3`oKwiwBCYzcN_FC|7qzyK!*wU%m|nFxz+*kQ(jUNWR|m`AP~HaR7bNcZsvf&sfyyzcfn(hcfwMy4K(VZ2@j%^L>}b$Pf<K80RUnHgD%t2@LP<a^8Ga`KR+yVZeg9A>W|JpK&rP8X=BL>+H}(R3VA@M5nd*$iC5>wavV^w3A{nlj&uSFQQ1i+0j(b_v30T2FB(uck<RWk&DU{@ecI%xnYa!-ffxxNa*3^4xXqf2XJ%y-2|XK%)AqS;GEdYk-zYmrMT)SEygjXFLAkCj>CVTKqS-k)#)9&;TWbf;GGu^$@;!V#+C=8A%6}k-=b&Yjn6FCr!}#)vY-!agK)W^0!bN~y%B9e|Uzba{un~k#Ppf4Mo18qe(@B^J4kBz@;(EqXJkE?BPqm98vpz>i;|}b=&6uJb3)(a|01@3*)W8lUJ!!eR8w~a$A(4^UzZR%z>K#t_3rG?H%t22B#e`LO!8*5*qgbi9YesJrpyq&mO;0oJzU_IcI-(J%L(Qv?K{DdW^eS~T4qY51nLZ$firqpmIFHU_BQuZg0Va7Ni>N`gs3q)xh7kdjZucS?ap-a^kBni)g5xip2#;u^6a(|~|9zboviW(vEzh9ryc1j$#;P7|q64V0c7U*qP!(Aqldpvga02-c!U%WT{$kr5w1C&3ekXoje^z>AgaSm8xHp|^_S{cS?N7y?nmoV#=)dHTE{$>#3vFUT7)5UGL?7F+b;uamD-vFQaq59?KLMbhRc?7is=%$O{%{7}k2uf?JuLel-~iJ+YHzy#)Y!tz@LQ%xbuv{jz?q99B=rNcP+`QgeuynueiUuUq5QZhX<aqa{eB0`^oJR~nak~xE2sGqhp_#_J*SgRp$6?d9A(QS_ZUjvi&QIUxZz$2uA`F5<A>Si5}lqM-1gsFx-P*n!5ML4*R45uIT3GUTw$^sT~id@Owe$`TxQ^mg~>*EnTwj1FYhNLJ&UsUu+f2?r*Cn5{Lm7M&J+6y@<B&7ABsCJQ2wf<Ysk_!OSd#?w*q4eRWPhVeL4~r8bn?^c~6FH06#Z_(3agd!8Nn)ANA@Dxl8l_N`s-oi^b32?sO+YhajC_S1;xdrh^eDh)Q1(#bP=6Pv5ez$ePxN<Y!Flk{n&cVwk*w2jO;zvCQI8nPjr7jAMqt_2x><r~@ZVE1?`|ymSHWJa4El58psTQKwH_rtaH<eJ-HNLXc_qmS8PoCyymt7HKeeJCt@5e@(&-rvsV5<^*>Q1g#9WFcG>EQyxwDbIHDpts`9A5n%>-UZG%K!DWs*B*P7ic4CKe9nP#!n3=1A^H+RH<7gUMMjjCEWnMIALwU>dwk{(A=_Y@5Yptd%t_CyeR0a>HjNS=?wu@YOQtkVQ#3l79EZqD9YozJB&8lf_T7sTVhTP<p0zG^9O?|R6Qp;gOXxfMZAwM(5`gJ(223ax29c#X4JUg4{O(4AjyQqWJ4{Y|j&vSOzKy5mR*h2J92pUx<u02BQp&#{wPaILu3&icXwp^zZ!ubY9MT|$a9=FO$qi~kD#^7?o#u=Qr>{4SJM3VaA9z8KA?-=c0<gN=yQ9N^bZ4c87Ca}ts_7lW9hjfAQCx|pI<M)2Ydt(e(SPDgvh>frle6~auinrgIOR8(oAvZD9?j`aFFPSzM`ZmUxU3#i^6*R}nC+3lKC%Mis+FF{;2=`~y+Gg>5UnrL6=pq=%m6brBC~9>Wv6+E4fHYM2$rb{VR_+5uWG4_I7%|FQRAGW%q!5XUWJ>U@R{M;!wVZ#~a-~n(W#h!}s}sX6=2(u0^DOq@>7Vw2&h*tMVCdCmNRADBSp)GT<%O;5MT-K*E%U?Sy6uZEN2`KpMT-911EQwH;DSGNNHBp1_s;3-;~7xo5G_nP;x|gvXwYu_MK;j)umH_)HAnuo8wQP#EVxdStW?0(B1;zwIEMMB7P%bH8}G=k1Qbe#;%B}3&`Lct5GRCK&0M_bNh`=o2nv@JTMjsU<mMrTV2q=sp0})i%$j{|KfzLh*iZm`SW=}h<&3*0)%iMrb7@-$!yXWz(CY+E8cYMw${H<^_!UYX1pv?)Cs5BI_J)E@&f&zBxQm!-)9nSumZ^ge26wAK;(VbiAy2t{H=^JRTfss{CKxY4$crz{R(6h2r=-F(%aze2Rm&B=^&zuNWsWal++^|Uv}W%lsY9V<F&lsv%}O1YIYe>+K6R+jO(H-MvOG>d-<%5aht$}qoPcp!pu^URu#q>&T)or6Rv68pQp)2`5hWMN&L!g3cu*Mrxlj>OJ7);^4+iUwqhS@oJJy%w5*y%wVxgeE5{>n#u!*YuXyWC9(Y`b+wiHjThWRY=jtsaKDaEqi#$pXkrg}NkfW=8GI7BS0S<~E-BojzZkJiPgGm;9ckZv}RDkIDu^tNAVsB40!hYyPYx32{ugn$NviISXHI`X^jw^0Z&>i@#!L8wX=daE@@+>WzhG=4d|gC9wAAS4}N17dyUqtF-|c)p>izI1%r8ks3S$~Sl^Pz=oZ(TSC+w;snOaLgdrAEHvo;erOyCri+AgPNdN5q{W69PI@xLCY|W(9?74XBE}v7@(Qk(8+Ceg-AoWrdQUJ@zGc2-hlZ~=OY?s*~p=}a}#cbJr-oG)~o))?W6jY7~bVw#PBrL9lVg}S>c0C-X_)HW8s56vsT8!GWCb)kDYH$!m^FQhBwPY8njV}H?SIi)m4N7NwVZN4(E<m^M;_vgF#a(X%K4RWW8orZIw0(Mi7E8Y3n|0!E{ZuHkTR2!y|WX1gIh;i86?y2dPi#uvqMh5}R3j395Bkojk_S#u#fQ6#0a3ac9G-$uSQ(v5YMX<BKcgXU3?jc!s@ZPpZ<wHw`e@6<3TB=Cs<Cj^zOsCzA6`4dvtLa74IF{=NtTuCqid?533_JQ@+64Vlg5nsTzDGwgn1dXMD}^7qi><&5v3m8+ZEcW3yzZnoY9h6AKkT6?g#2TT+OgD>n0ZDRo;LbnP8R(kptD~<}w0c#r_rXd6IA%~!1?r3BnTuf7c(QF1UM@H0Hi0}%1;rQHR2%30j?v0aA{7C=<#Bp4bLBOFo+Ah(b$5r=k*Y*WumY&axUAO1od=#IC_K8J!ib%Sp{G5mV9nvaO((7q;(lk`Rp^HtM$leDLsrTjdRGFO6OHZ}InqUKZf0kMl$+W9NjysN)1TagN{e+v&Q<e^oV>wy%pm#wCRl`CxiLYy3JtNrQWJhfY`hA8?V1xp?svDNColeEnzPfH{mpFxDcx>G^+z=r%k|Q(Qf})*ZaDd8ctkf2A9b<6@8LB$bAMqNq49ATZQKYUa1h49SrlXf4W*?)lHM$ac-(F(}b?E@aIALU-yM2`a4kV`v?bhcU7^Vt{q3DEX^i4`{Mf(UOT*rtLa7JttzjC=ZTsMh!qeLSJlmPHYruLC=A7UsP0k<M5MkWmZ2Yo@VmD&$l@DDc>Bn9WL`sfmZUGjsE&M-I)u1pywYo;=N(atQ0%E%a4g891t?#+lwrWNnfM<z)(H(v+I?+T!JsEvZthR;X+aOwF5^gAe)w^X<D#tcu~Q|!R!(qfTc!$0fNVPBoVT@`FhNRrXx3P)XlaE1Cu&%voFmUm?0*T1?HB}z+WP5EU_POEQyDxAZ^B4jc1Bay=equt2@WNfu)UR1fi7@XtQbjAZKLGvoZwcmkWZE}7g!OtnrWpN>ktyd$f*+e+97TmXJbNw4hg{Vp%<ZsK5N4AE%_hJraFAa=H%rRjbi;{uyOM@^TyHuSC53E)Y*x#LWKrS;WQKJp>z-E$YZWN)c;zinOg-j_}!ktZ&#_3Rb3uR0-0o!NAC{{N_B=ca~<RC2c0$Ad##LewBR74;*P#OOY6rCgs5iIT}O6KXS<I*UNL@GDTI9E@3A5k>dy_0V?KA<Er5FuLGV60>6!cChbZ_K0FJu=6ivc?vMP!}w~8HPHCSLX=dv+pG^=R(4+3C_(YHS(u72q#0BBmuJTV=q6voCVk=0OWxi!BwIpCi7La9MC2pr2|oCg<%mbhTIs8kt1H_6e*%^1dOYfWmqHg=K7DGUL?Roi|kY&WNgps^%H{f*oyK)G7L+`kGq+dTv}{2r7L1}9%=|x_5qK1E*VTZ-qCg%?;g-+cYjRBBQEOfFMEP1+q0>*H6XB2!}O!xb{2;<0*#Qo-)`Dif{BCBZk~U}2MM&qgV!o#yC0-)<3cWwzkVoITInK<*s=aDK<I-IMTzc#ewpWjgXow+f8I^?83G<%!=_lhRu9t?16L=r{P~ETvP|`-z7ulmL)S<f3l^P-fox8p*~8>p(Bg%qz*D>#?Gb+O9?bJyjfJ(=A^FcPhlNVB`;FY|Rs^&i7Vz6!p0gPS2!nu(O0RYBbw)9!U#jnW0oF^Be(vcGb~QNhk@X9=X8B$Y!p#@{n%~fQ28A9*mffl}nB@j$=Wa5amfvH*ptUkS6HF-}hWPR;CG$m<5onsAYCceI#hJ1iPFh7<n$ksJp$&b8=`PUgX$WwVkhL^uKg^Vx4Z_z<5hi=3)+AS>o}vwOiBy9_vs~{l*2>H02Og92nEHd8#45#Ci#>^TuM5uX(XJ5J>A_56moX*ke7wuX+4)Kv4j3nRdMJk9OrG<ApvENHZD{sUy2@N2k_ydg@yMVL5=GnYKUWcJn$E)|es=DIDR|fm(nDndJ_aK<_lz31idANJDus<IP^(wFc}=bSjuby(7GFS?gydxS+Swg1-OdYaZ%LS-yGbz}A^Dk{|2VCT_ZGS6!7H05N)UDi{0)V!?-OCwnF^2tGn0j<2wuD;P-f|TT4wJoxVcuVun~X@C<%(Ys~S-qJpE*3*C#D{Sx$2_^VC0BsSUGM5OeXQG2g0JO@Z0`@?M05h?m_l0*!T{eCR9@+OkSxmZzb@P1N;sz3j>2RbmQzn^_IEHN8%VhCAC(x-ibZ_^mt)bd(kV_#jsrPm?<G5S3u(19zu#hO0?0lsoYoj}YY7sIAXHj~7yV4AYFC8m!Lg#=FDA*}a}SWZNzOagkURleM3ggN6WBaAK92z&wd=z)oSE>dh3wJ)#bw1<eb?3_rWpMHiQFd3(W4+9fvKwGrzsca5EVj?5Qiu*Po^rv=0uqRm!|>zvd9w}}gUV~OqFz{D()&Ge4ONj|nptE#tp=)P($+5MNPRio20rXNQU39z8;A1FrbT4$sXMOs+A1R{uUMAlDaHpohel3RQw@@vK8)p>(Y*=h-W{7$$GyhNXdJ3#_GTlU-g@{uJUBY0mNK1_8)6poRfbs%%Xx+3^_eV@w!l@)g97-kDK5Hcg=uoMc>NUkd}8zfmU`9_ZZ7>*m<tk8$z=sAkGZG?zFS>p~rmGw-zi;*=T2Cnr3OA4sOvU<{{3GxozIzUELT!A`2@%!2NuygTW&0bzIvcJs2bHcj{cL$vYzU49q&4!`&x)!;K4m0VnjYo0m1{Qrar~&%nizAiDOZ>q76A`kP1nD|UtXG-G7$90yNR5CCCH8j`*^X#QobHA8f$|0HN><wl4!)FL#*t^1UTz{Z;sScL%~1r@Orz(e+vF*aR3M-XXkR(}c6fE#Sopl2%e>N6nxOz+%GMe-^&y30LQG2QF)|$BfK^9(dKwOgwx9xsCBfYj%x5-3aR)^;EykM+c2JVn8F&iu@usO*M?aB-Oz4B9#G+_%tVvV?m4fjH=jf0ug-8&CY2~Ojp?QIj4XZwfGDsvPS6y``{1{)Qxrr?!Ro>K!6<1OMf@XM03tbfFZ*wYTy9VAbrIm|zgMiGjZvU>JN(Ic#sg&K)&+t`08z|>lL2g3(%CEI780W;@L!1<4F^U=nYQKB{Vs&7NmFt78tVd!97zR@Z!7O3JytZR$*L86?<rA@fA=C+p0cOX)Ok8N+DKM`hrKRG~48CVvZ?%p;k2{<>uM!J4kaq6Ah9gAIiXj<u^)<8cS!F8=Ur0{oTp-S*N@&|_pbJ=)Q1R;bHxlt6rtJ8;$$0^cLio}aOr<{~MmCg%?3ctClTNvN`F)FkbO<2`bYo_vUZb}n2yh`{TXc0Axe;MEqWo`pH&Wx%>5Gf*HDY^0mlA8B1|n5USQCVun8&6_X|>Q-!>2wHnqkn>3X&jQFLQ#LkOl*+L;)Tx#_9n3kr8D>a|O;egMzttX;tAeeBDwJ)vJT1vi?41l?;9_E?7j^<@m8-nQ#v$W+T_FlZ_29WjHyQtaVn1E;}2M{t$&?dbG@86N@QO>t5Ok7qWkWe5feB#EOOu6L}g0e#|&v0k3htVr)QJTB87~g7!#Dt063(BAp_A!5heA1!|MG;D`gG!Ug_}sG83Q-i_B4Yui#IT~Z<uq9-C^@1^U!oHHxup|4eUAD5PXO1IuHP|uA=^NQtg%bt7C&DgPs#UAORbGPSp&oVJQa~F6NaPjDx9(eh<P-RQrLWB<$dqpl0mrH6ps?+kNn~|W_#c2~3jZPz}V4hX~k<BC8)5?;`U6COgur!23$`m;kfu5AuCfO;eTTLem5R-(ah7_+KUQ6S8W{Aq-lLVHZAR@u~N3DcoE)~uN7X}MSCgp&{)B%y)gjeg-E4fe*McHnsdl0b#!S(^A8cgdtL6PPkSV04e@_&z$wF@O{n8E((Km$rfKri_W9xcS9A%9l(Z(<At#T2h%I=Y<x`Bf56bIlE&NogqY=|?;XO<XdZaKP{hoDwqcLk9Q*>-Pj$YRHWy;&MDWP%4?`k4dYETWgTCqo>iskpxbC_n3k8HNt;}8-rBlDdm20#t=eb?8wXBF2e8!VU0j>1U@mhbo3<&StX1BFCap@@SA=nL?!d-p0@s9!PF$=gENWo4Btsn`~e~#%(&<RvSXKVdlV7T9oN*+2z3637#C-6yOgMHD1ol-q#!O<gUJrp7D_?us`)pvB7M)%ZHQnAAh}TD+~w2HXAI`HH3h#%3L0&&;ccvG5-UohPnbQjxuV)NP4^3|rFhr8eRrmLWI^lnYt{VAau<9qYZ-p}C$qq<w*')).decode("utf-8"))

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
