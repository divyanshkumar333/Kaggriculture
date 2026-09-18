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
    'c%0RpPp=)vjm5u8pmi3JW!cW`Wa(urM79k5iI6b_!@y)Pz#y~m%x;kHK9Zi^?e6Lyc@9~1C1>U9cXhj~SS%KKc*y$c|L*<AFTei%Z@=FAm*4$#@5e_kU*3EB``_LB&tLxg-~Z?RpWgq^-+%e_zy9{WAO7zjzyDq72S45W_Vr(X{_(~0C$AsBy7%s@H{abndjH}6m+$`JPxroi`r_uE@#+0j9{uq2`$x~-KjiWAH}4+--@N?p=H|zDAHKYN_wwfE$@_1<zj^ljhj$+yp1!#o(!<?5&l7$6_|LC@JidIJ^iTKR+`N2sJJjvd<41SH-+p}@;H~&Zk-fZm_G~|}KZcWe5KiWcYzmh}7$)(<^B1qayB+cF<J}t56XI!{UVkT-$_u}J{q)(BpWpretJfD%I`2CDt~ASMj~?Ib*Xq9i;>&MYOWu9`!>erp$1!XQ^QZUA>A&{wpC2^x(W{#m$t!l+>Ad3Zp9hk>%<NV(hBut#TsABGhTR<Jm4;@xdjan28C8KfZtuwDSyT_2*~{mz@0J9mxIjHf+jld(ylRDZ?B@WYyOMTnMt^(#^|Zs4=K}4p#aUDnn%4FRl;SwUjv`)$yVLsQkDayIA0MYxnpeMu;Fhc3WfC`!rj;(A56N)p$t6TL{f6TYLa#Db*7o{*${*ei|2H?(*i@?@K7aP?=JBha|8(=>)zfEB|Ls;Wz~d3mAy?Ou6{;!>N<8Lrpw@>TZ<cA<H70Vg%vV^-kI!x>q4&$aB)djo=^H=&P_O$#ja1x)-8+>zf&ynq0)UOLJuAP!Z`!#W*Lg$?-edx}-$5QWC(koe6!1pq1U@kw{#V}mok4_YgS2^2v!~3?uj!l=JXCjB+2J!euuVeN8E|p!W+a4C4g}O6)hUv+ccL}meX!pi<4*d0$qixM#58enqlK{sEMSthm0b{zuL!dP*(^9bnsLB_19*hJ@1MST`Rc`^H{ag8c=6W{c=>PTWGx4T1iSQik27R{{)OXx{Ivd@FC59%xqj6ne${Dz0Zex4-f(_EQ{0erz*45)E8U3v#I)wIGt80v76qG#H(Afd5IA>0RvfQ-N|38)2@e;VvlAG2Pb(E}N-xG&V^0!fohP3>u!1v2?$T!G$K+PS80{W5LaLpyZ98T}n>)VG^^o17(<12wc7&Yo@)EgW?v$N!Y}51BfAZAHo8up67qb_M+b`^gdHPtW3RaLd&Sq%p$zy!~L1iDk_)9GV$e0E#N1WPhy+R+#MH%61@NvZ?DO%hUNYEMbow1gC?>D)wB~alogQ}c%KaSuA;=9x&mV*%!n>U9jwgbDq$dzydm$|$2c|^QeR&hwb$jxydI~@s@-*|l&D@1=bQYceN7g9fG!>_aV^~I<{+COU}EbJnAp>P^zTdwP>05$W#)H%>{t}qU6yeW0C#Pd?-EBRN}stQ``grrIR3X=AMX`8#}$(Vec-NC&bf485ecFgIy>S={-5#lyWxhkDAGhtmECEOmV0sT!<Ck!NH_VjJzH)7PahvlBrZrMsAfC2{LfK=9To!?UhyFMSH^dPi=)k8iAUig)t+9jD?+C$9J!rH3zm<oC&(g)KB5|wNOxty^~={``OO2>QEcMy1Dl~bgbA&U6>d<gQ$CLAZsGPToVHk_Dk3YCAaB$`%xYE|co9vA6^^}r`Dp8puDMD9rLHsJH;@Be#SCWxoURwwxGkbDBC1<i~A9UcgU)L(dq)Ao;xCZgzN>wtQD;HGfJm!!eh?)iXJj!w()C^fr0KEwLIs;-Jt+0~Y+74LE!CLFJi`{~_zmit_lPw^J<{oe{Gbo+(}gFf#f=u&zw-u5u^bM5uv3^-RaAH79i9t+Zzn0B3H0l5fR<D<C(lW-Xi!HAgGkeY1wFtlfF9#X1-AXQ-#F~W-GN9RumQ6&9?s>4)VgL9<(uF&gfs39C>Y{6{umVFWl2OR~b^slpmBGHL?+KN`qQ_Lw%Dro@@VXWwr(29|+gF_dn_te%yt{y8iIkM#WuOWIRc(UnZiBPGcJ$bAl()h;dFuD84evU3}s5Jp^#f-t-nnm=^hE)>1Ir_eg8Utth)~^ZfD;&|LTu+|<Yc#aR2ymu(<Bnu0cI(#|i#mtY_bcA)eu7>Jle$nJL$wU73EPh$WE}Q%!^cJ<pg|?rad4v^Pyp%F<CalIhse<k0adV-1;NRvi;BqaKAZ}hP)&rLa$>Er`*?s86)I-o=kV-JV&J$<m+t2JQHswpKaK`y@P<2v9M|fiR!U{t+Cnb$_Wt;Q69e+;FLa!roUz8+NE`M!>p&jmidvT<jt+Vpzjt0MmpF7I&l|wiJPb?Fncls8TN?=WJp~gPAadN8KhSX+#LELuP21~!;TV{VVI!p-=q7TBsS9i%I6DaiIu{kbth9oe?>zWP^At5QbPUkhYjyT1;Lx;tjnQinFk3)M%JZzWPnT<HT#{zLw9&@xE=Q~;SO8&rvCREHyw!n<^JxJ^UWAp%bibR__fMbwnFZ4cmA)A4R3%cX)vr4<$UPh*CYi~6<&+c^Z%jlU74ixXgY@YN_5bMb7_o<c9w~DV94*%?<{?iIu51cZP*CKTLtm}o0SSk~qGBd$fhKJVt#xOj*gfmWkiDHePHz~6<dbrnmQeWcedMhUDw}G=bT$ri0(t1ZBKgK%G5R$|WbK&|40Ko_jKDq-Tt_iEOGJMxw7h6z;>>*vg2ENS9(iYnmx#D<vShJdB)Qud+HNi=k8qvaVsPU&!O+_=Udu&_k*~+}yhr63Nq*mac=$$*{h*<rCd6@N5X)tp+%^o3;J#{3itZlyI-71kl0tS%HI$-+JZ7`RKU`6{GIsy-UuKM7k<C_=?;`#Q9u1OA)Tjy*SQUh6OE(t4g@<TXnsAlbk<Ud4*hEZ8V#w2$1xYlfN3N>WC0s4MKf_-)k*+O<x0^8#Xb3Bw431SqREv|poQsoLF-?ajxTz+;N~w}Kn5s$QwrA}<hlR5&0ky)Tgv6wiUi-%(9)kqf9{wUKHeEG7KPyF$dV{cIr$;P$n$`x+V;~n642t0Y0`z|LwLU`cAv0!kVl7t9b{C!(#Nw4U28TDz-;Tcvzff7?{8}W7xa!i41mt0*rQ%a3!NlSpopp6;k0gTY7&gTz*uLL(5+X2an&&<9Rk|n6*FYZD{wg~|U~=`Hq5SBUBqx+UvV2mBl@o_1V6?*0h!Q~L9vG;|WZ#G?9!yUnkS;o-7I0c~#VJU}I5`%SpYEn~O&10=ZZkKCxEQm@(Hp#I&Q0KNCakEiLYy?v03A=kC-LyUQW`6egM^MI=Fx^wjGS3;I(k|p(DCtWDv*~!l=Gi>g4Y2N(`sKAMI_HmKx@4I5J%^jA<twAK#N9PR0tlKfCCo|tc~$Gt`yo!fi@%skID|Fh~BkmB9VIcku64leac8y@)(Y6Vf)fZF@p3x1hfi>s!DkYO*Q8+VnnL-y3LhHs*yW-EtC9!jfzn#l8b{<<Vd+_B1Ma)B;8@eNO&>tKP`b|PCx>tLL_;CgwQrr35aqog2uHEAnr;@g)^*#@3THHw#}@mHjo8_4`UFx6rS6zm5?hLcWOHAv_7v#RdLvGOU`w%Iffkzrr`BF@q|%twYf$!-kXUw&W244l6-{ZUYp@ldcmF^ZM$36b%L}xsny@*a-yyzrY;d{Mogon|ECV`)nttDe(X>iR$E}YGw42BiSD<5dvII6$iCcnC>muz5P-<lox~J0+r@GT1vx8jbg?abr{Ke+L(dJY!c9<hDJn*~DvrUzsL-h^6s2}tr*HVFg>dBmUw(Nw+r?mm&4X(ydb4=lnfPO89~EyM3Ru-S)v;Q8LHjDN7{-zVx2Ap+W|f*g)mk`|BMvC0X^v+?R9orgUEz(^K0{DMHs|Q8FG@Ct6tJ92QMy*>ZM3B@bPIS4!A2C|$j3rX$n&-CU&VcAsRv6uu4a#29;0Us1=JFBMDr_Ft!#*80y)@pg66h;KOADk7@F?_cF(eC?a2xAs7jsT26aG!Iwfp!qi%_m5E_#qY+foO+a5YBet%C9jEb-iFC%cSlKWa>B@jfc>OIUDS*J{V)CvmZJ(Zwt{PjW2M9mYe8ZP$sHoE<%0T9OdEaw8OXw6W}`eXa@_dhWyA&stOm5-k^`Cq7ZiL2JGlN&Afe@Hw!ziYjl7oEuW=d^RN@Iv_t{7v39v+~OolXg3)rSSR9;jO>v$%&2gG(;gsJJ+*Wr8Ads#rv(!bjydFds0pw75WgUOkt8-?F>R?Xp21N&JgHvd5uJW0GMi&P+dO(PMGJUuAqYCe8ll@R}oUc8ljzAv!qs=GMVKKk_)Y?EaE0x?!fkuUs}z%{V{EAxZuK)Mqdb-VK9ms=X)VKIbr>`Yvr@u_cvoc)fR%{c>0^w7tbp79iQ=uS^?%!zMAON?WuOSNe;$}{uOC%+VTy=ZAIw|(3jWctuh-jcO1kQnn!L;s|~}|?xlx83!JMIlwvsjNAo6Folllo1^WWgVUp7w(b5oGX1yB!pt17~d{#<r9~D=zJgR|$*iIrHs*>T$Gqtp79QG<^X6D^h8`BPRF2_6&iLO}9QO$KRPc%=+V2G;9*4xpD+>)k;zfL?nBJ|`%H>4t=sX*~}LRv4e<BtyPE!wNn-VLb#hmA9RT=&A@sCoXH$^$aZc0W(lHnN^8#v-z|NiX>6wWRjl5Zp3#y|P7UVkb`cloWI9)<A^Y=|x*&yO&Wvdc};#Oy3Z9-Y+99$jtAy)-=`blSaq%sV$=%p^E=z+tv?ya_p}8%`k;d3x1mvPC-SV6pneUkOD4rJ8lR7`XmY8<vQ>9`!;T%Qo$ig(22jN_}v`BNg8_eZ)>O2!-Lu%l!h!xrR{rO#wF9(E2_$DN1$E6JMG^UHk08M7>rM?EdBjOs~<IeR9xGO>$PyJr7g@uhj1q6TA|72b>T;a4IF&<vlyTtaSN)eY-53p-!eQUT0iC)Ta`R-WJd*1&E3EX7Z(QYVdk?`nov*L81+gkucO`#N{R(K!j<t_c{CiPwgn~fUOO-COB7qIA`mdyu1|>cTLso279R`f#j|N=3yg2U{flaAl-g$4jVLZ5i8V$Ak!=cR)90;-Jg23*siPIxfSUy`Vb{TN+YH7hyQ!gD&bMmkpB6Agss!o!AdjEoi^vOPk`+nvG+3|qXA2_qG3p;8v1mu>?D)gb-VD8jBcVg5S>gT|a75j9rbp(rQsrhwKWFlK5J!7LQ@KihPb<YQrlFDy4)#`|0R%H^69Eq4Pna7Oj)Nc73Xk(p(?CfI^gO(+rW#@Q83jldz_>DSl0^l4g&n$}OACtHry!uN7*SUN8d*_<q7yxW!=TJTayPWEZaIt*Hv6t{86urMY(K#^DFvcbn}gZln{0nb&_nez;Y}qB<J59R=1Nz`NPI(8TA13VlJe<_2o6S&j)+g4NV~n(19|1l0^WwCAEd(KlTOSDlL3*4@#HIUJ`~@rK=TRQa{vX@9EB~=3=xLfLVFj}&dJ;vMW(pPP{WL>3WKVHD$7@J&g3TOlD$ed1fv;<NW$4Pk%<=Z8lWOMa3B?NPX#C0!6fs6OE8G(V(<^+Nzh`5z6A%%aQ_w@7_00dY8O0=^q``$jRibDpVTn~haZ~=nCh9|aBFdcDxVfy6Z@MkXz5({dIa`Ddd@YgT~>5gDAm1)HD1<4As=3)lL3@o*rpxZEa<?i%=hfav?Ni%1<h#;VyL2#Lg2qtu02gsQqg*Mv2<5kOZ_2OeMH7=!utRxQE}166yqq@LSKjlnoBN^k)7{1T1b?{Y@DXUdfoR+-q<nGdcZYL1wx^h=%oxk4v}XcEqkphXNe3&=#lqqs5D8d=%PPT-6~J;2!+3X%zXi^5+hxFy|K=Cjs=sg1RAc0^?s*4)sb)&9i>mTjZ+b0m5*gmH$~&Yee^toP#7#}G|jY{m1d)NcG0Y}F#HP_eHG$t=ZetL6jWr2t_In=i%W6uo-sf@6)Wi;Ooe&$HFJ#}_G{coBKeVpGJNeo37+vB3r#*_P0d>V&dLHAFILYBWYCLCc{NESE%sNy-Jj<Sig2n-39(z|mF)fGDA)DWL)i-JF56@;9ez9X!>Q@I6(`?;F4ug$a=sx-)c8W-@<cMXa(_uw%p&jv4l>6fH#V_ias}sSRMw$;K1_#Ym2w@$5~|=OG9e91uy%_JcqwzHV%t@y#;BAG`}8wo8%LYQO2wY`Q{OZR+NvzfP{m;;=Rs_9QN)27%{|f6$s{b>zJ!|>nuG?c1Z7!FtUj4cEN*`NgIA!mTgv_#*tK%%_K*r!Q4$Hp^aI!&A5Ahqn+P4%Zul5R30<+p9RM|U-|Cp{5Xt&u6bsxT)r8l9nF+chD_;<9w~h7Pmj)F8XP#3#c8rHSRwG7>yH-g~K=7cFQm$wyOja>(2W=c*giHi#LCsrgpTuskQrzP+J~?jldFrkf@-EU|oiim>!ZxNAM`4N7u(=g?!t9fhqb~c?(}br~u3A*%Opq>8wM9s%#MQP3evM)%-77-$&(p^qI$inC#Jp^7NvQ`Vug>Krd4;#g?h~`oT2R3r6+o4$y7HD49A{r7<1U-1C=BA7ylN^0k;Bj^=_wJd+!Z>aN&-vXAx2iHfP}=Hu+Cn`po4TviFw|ss(32hWaUnw!mTAwKT7aYk}@-l;dKJ1Tf^Y~QJj~uQHDLFX{sW&-N%bjxK77jMy3wZ_A3unt!G|(DOV3l+=HG5^~EKn6+VgVg9Wn8^eLKlQo&5IT=(3@gCRGXth{O4E>nHYi^L+r@KNSqdyKQM008PWJQi8FVY#J8C6`RqmT5-Yj7zB#)DtvB^!j75wOtjpQaRQi9B`5O5P;vpjFVh1;ZWG-BVj`eLo&HAu@fPA(7fftf-F2Z`m{bH<ZT*(q;~K4^=U?pX$X)}ytiI1HCCB<wwZ3<l!zX)wEpmR@1h)f<JK`XuDH;c+r$l6bCp?Znlyb0>+u`Btw=(K5*0LmEB0L_DXoDfpF<|Tu2QdaU_<qKRo9;iu(JXxTI^IHewOf#JdED$*Bs%{8FDFv8RsuLmue-zMh;)&2f{6Jdklxme)H`44<Af@x%FqkA?(rFeCNy~H@Jm-^fKD1L1$BS6OT{fXe?Up%mnPEGzl!aX@sF?=#Vd@T=sJuOhjAJBMtw!W9oxAQDbsP@J<CVJ}2}+L~IV&I?RcKEc|}7Y1M{}Riw~6*pt&X;8h1$&A4bRh{kRflS2g~OI7IDquNZ{wSN~4wef3>tmIJ{PEDz9h`%f;yi2j;j>!q?e;h59y#KJg%F<P%B*fP;+dT{t5hR#GrB*!4^S~rkGREFzakoyT^ZeGSa)BBg{8Qn@4MUB5$+E_ptT;-1iX%GUZ&B(=X3TV4d)5)LjM#}l?Yznr4Z?v4BND2)w19%VPhYe$d6%t1N?{Mg@2-s>@{Vq0D$+2~fdCytyJip~WW~QCiUXPOgS^JG9-42738z)6$FT?TR`7(QGNk3uW7wn5h5h7@7fO-cv5JABmmVSCZ&>cPXx}>a;{+0`h|aU9tCu3G)Z#vV{^mlI<fHY|+*NnFbY%DxX~@7ea6PkVQW8^KOvW6iwW>3d^pcGBK~;LDF#b6@WB7oobXiavOp?R-_KB;sbP8q`*mKl6Cr|o;l_VBM@r_8VMgf7<-#cE-gb^s_6Kr|uuhr^N<>LahXa!nZ8HETO?UYhvfNPyS2xN^r-lr4Z{mTpYPDC#WHSfCH9#z3{<Rbsp-(54QAUpwdhlre0O}z3*3mx-C5z@D>pFVr?^E)5x)$5cRSg3%^CxseXv|AV~ynDvuo6%8=w8BW;<*@c;Z6?ZS?_S2XD?gbdK7a<T^W`y16!_+;&h60mW4ou|2tEV(qdYpN$;f#=MI#YBEDIJ)VT#59DjP}ZWEi4XmrXM`Wal!GWJNgQJu;K-mWg-@aMlJY1B)jS331$5_rBUX2z!p&CswE#kxFiBUnq+=7>CozUCqi>v4Myv(3OWz?Iw5{6n!Jlt-J<h10-oO?SWHcxl(nR1RQgQXP)~WyNd2N%fWWgj_KiU4{oi{6$*`A_UScAkJr6dGQHq&x-7bk+cZwi3gOPGw8_A<#&#72xq=a($Hf_er8FG@f|2$cbU+coPjLac46Dr`QlP3x%N#Zp^gYR|rWHTLK}Z;ntRcMQ>6y5%3=Tx2Iv2~D+Me8P7E;Jj+TE?SoZ5mcztZgt$X$;eXj4JVzWZ_2U{ob1y)eBVC-g%sh>tkS{B$n%(QWLE%f0$H3U38S)URa|$|oIv2_AU69))JAVX53ztolhmqT}LXT;2L(dA`cvk>HJT$=OG%XEbN5<u@YyWoE24RV+GE^V=i*z`V1u#7QO3tUPS>1X!`{QJ7h|xEJdR8v+F-6&=Xp;Qcr*`gfLNo9kksHyPsr<h`H%*il2bpSu`V95P1+@(y$(q`TP&e~zQGeOdq^th&*zUm6;BXj~34JRJ3+3NZxF{c6~fc`RYoT8J&O?A|=#N9KR?!3$swwln02XJkz<6dF`PKumVeC%vFgBOdDC5`dzNv<o8`Xfd9N3I^eSdQO;!QwksxAg<a3lmN2w-2aMWEvWRx0Q=022LoN^v_v7G>g6UtnK1iZA$)wA(n6zvH)6VoX+?W?)cB+5R4K5@Sk77aJW3tVX5}9$c`Guq<tQG>Cpq*%G#Zf<R)rw=M^F=QOIKl(7@R0oi>Ru+0={WR4;AD-*hUm@7jBL@eqZ3|*z`17IzAgO(krmLM1_y&g}TVf;5tUyiKex3rK*vib88YsqYZN(macsu<1^7cLK$<z1`R#k%{)|2$5CbGyb+mrM9<F+&7@teW+FtY$gZkXvEGy!O1G$jg!hH&(NSaQpVnNr0}6CYpILG&bF?sMoJDku5Z(pM)hY;wE>LJ)HqJR9lrA?Nry?AuQ%94Qv2{H*?4MHN2GSJq`_sP^6GMnR?~;(yhj3K1dvh>RuoaFBPb<b8AN3h=R1!@5x6Z()${8(C^uc%_R4W|G4Z#>bFZb)Tkq{nRd`_reR_Q{W`okdNu$vc0kGfs~qJNzz|32|g)M(onOyt<>%pga+e(O1P66Lxrd^znpL;#9HB62-)Jo{kd77$Ze^&#<+0!I!GoxEUzyzto67`-W#XWQAzTB#}4AdD;j<iOA4GPs=)<fca-Q?!W+&H*#Hj5O*lOAIZpXrsp+(VU*h70`|6Wk&Cv#0c+FQFBvd@K&qvY%V5$q+Q{(MDOk90zWgu%$<VTAP7kdm^zyqOf1Kj8ui-Mm#Hg|B?OC*=R|l+*?>HZ?6u>|3mHyE=~x$Y*wb|FF-6EB3~r=&G(f{9<J3Vhn&#NQ+}i%CkAYxmSas>6rE6FzodZJ4im-JJz>cJy-9|*+f=G~;O}wo!eNs4db;v+EK@>Vz&U`E9R2gLR#r+wgnH(WXayD{&OW;8697JmmVULJvtf_Q;hS`AY7DM6Ba}DYHPbT=>p~;;p<}&;z;>0~r=hAqXb&(*Of77G8Dc*Q-v^Fb76WI#GP5gW{-W8o(1Y51|-zzx6&CsNDHD=uv%A6D^nLD5j^_Ma%6=}<5prdN_#h-BEh)TWG*)nF(N(??coGnLNxD439a~hBA0=q<_0yf%l%-Vd-5~*cSE3BQ$ZdGhUMt~AY2_<h;^AUf8k0PB9FO%KSWz6@b0aCdf8Ot3`tc<N;0V=I_nz%<)r;nC#q{#J4i+L({yZVrX2rZYepCssSz}s?Vk}>Zd<(WXb<}^)#C`PN{Fe&i6QLiRQAFRs=l%kf%-veS7$$u!onPk-|Bp1!Hll@`!?QQ@4DH~T!1$Hj)WpG?Pfg`yU2Qm#Nv~kwD3D%i7Zxl5)FIo>2^|r}Pyu5{*PjjFLH=PmD<fxDVfab!uAkyCT3tWwwmmv$VOFPkp<utF6aECebX(Zl>y`^bYCx3pf@s))Y=hdj!uTWixt*!5Jb?V73%(RUN1<DO*IUx}xUX{StD)keUnm()jTdRAPzZ@I8+<~+{XFII|&t9CNwF#O|^mW^C+3U$3>=N!5`WqtdlAg<4WS}s}+@X{V3x`di@W%6zW!{RZ#z}y7H1-_!$m#Db*3^f=u&eobT7Lmm12>gd5g9J=E&I^DDX~O{+o5sN)Yxp@4005EPe6(ixAa>@X_S3p#D|kKxS3F1gRSf@TZ{=PN-ZHBpkqfq$Ed}M6m5Yb<xm|e)ss?2{Isf_O<!*Zjq?lCoXiz0E>p$Y2?68&!wBD}^rI@0Dp@}^yg6pkt&vk8izfM@NmKDqHK{{hLk@oHN-@F24mo9Q!mGf$jSGLclol5bj3E_46$kF4_i4f!7iWhvgtdv0DLy6xOt*7CTIx3^cyKuz4Pma+AEWtnf@cv)R)=;Jiwpfsv}pTyoF0?ekoo^j^n33BU^u6*tE1NShoXPa?$pw>wCo>8Wr+`lUwR>VrP`1t(`%@H{^*$)vlVuM`PR;;iq09z-pi0w(wp#5h(@J5QF-G=udZ?@iS$fGvE`IjOFjyLIMJa$b#Z+keM)%X$G<r@8M>>su87CzU8W*7AKcp>A;v9g)g<+_LfA_qd@)WWDrhn(IT<Wa+<gnQHVOfv1ZM@Np1``-={3e%Qfc!V)4ZtpZE#|Kga{k>h%97RrOb-mBfw3?ZPAC1QLx^=x=FMf7aD|P*Sx0!8#1sfbt6L=YQZwbemk2FOKn!-2S)0Vl+jR3k@Krutsv8>Z`dTyOH3;Xz^u9<C$A)EE?BIEw_1W?Hk3+4`V{u%gJu8D%9)Y5%**<ms^c6Y+jjzEZ_{Tj9B(PTI|Iy1B581W{TH=C%Gb-wpyVQVN0+B5?9oB-=gfV2muUa1c&m4?mZk0RR}hP)+$Y6EFm4CV(3AV=LspbJ=x8_!Rm^}{46h{Ye4sUOL~ysou!%sZbU^|mr9zn+_u6a_9l4Min^Byy+>vcayHKrDD~xm*%d0d59Ues-$i5c?!xW$He`G`#Zc$}NaxV6xD#@DRcX&$P_16l|NIS`D+t?;lR?LWF^sRzEWdT##L7!J3i@NsBO~-~M$Ke=7bKd?(@Qd-dQkjv{a^K57%ab=KTo>jRWm$j`LtnGnF-DQAXv0~Zf2$Cq$SY?Ak3<pjE;wGV74y1~&EY1tpgIg_pmy7!O9@qIVChaOh|5H!jLP#L`Ct%F7NXyBu3n+zL5&RWg;U~RXm2jenNLX%KueBPYiri4<e&1ObNr+>8DPV?OuGZA4AVGQ)w~`aQJjS=4Eof*nm{Bl;-g`lzZ_8oH5W%GjVkHRsMa=jI3*e&#M&QNR0b<N;EEp_pGf5m;g%4K)Q8jXIzPUTz4Vgu0&tot6dEN*sV<5NaZZ=OX|9@e7=AMEHa#UT#p90IAek1cZ3MZXV-_kqN>RA;9n!N6kq}iHF`m!_<+uUz@Y@W$Re%_cky`XCYg1Xrl^CJe=AyE$-`8|buDFM6E;Px_T8Nn)WPrR{uIhLB6B^3O`-WbqAb?o>Vps_2C_hM5IZ#@;oarMrdttPaF=n7*Tu%LAa?$8jgMT#xWH98-YVjwhUq=Jp4*b2xbxF#(i;xd&2e!bsNQpZYNGN?7e8!|8=<dxbpw3h5`Q1eOe5n;tKPZRPZXliiVq7FkvAGo?a2-??#M^(o{eRqfXh8')).decode("utf-8"))

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
