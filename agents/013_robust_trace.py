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
    'c%0RpPp=)vjm5u8pmi3JW!cW`Wa(urM79k5iI6b_!@y)Pz#y~m%x;kHK9Zi^?e6Lyc@9~1C1>U9cXhj~SS%KKc*y$c|L*<AFTei%Z@=FAm*4$#@5e_kU*3EB``_LB&tLxg-~Z?RpWgq^-+%e_zy9{W@Bi<od*8nP>(4*Fc>d(|<5&0Ief8$Mn@8_I-2d|3Km6(5cTZp3+%rDCf6AjDo__!6+53k)e*WhDBjB5t-`(8&`0m4(m+xNQ+&p>z&G$FYp8xRf!^6`zcSCx(d*|DK{Qh^xi9UV&=hr_TU%pNHr+aU1UcR~=>h|gJqr2g6zdjD|R(zw#Ufw)=wjbCZ!^u1dC-X%%h07ugllbBJi&x*>j(GR+ZjI>)@ib1azmrSlh2Oq@`s~Ti@BaVQ>x(Fzcb$G$n&q=ck8k#Cb>DyS<+rRQ@4o)w)wY1+7&e9Z)BEN0Uwik@4;uOC)y<3K6+7*8UUB!&14&+HcB>h~8%}aoVmz4@e#35#^GZWA+`Rzz^^B^(9JhDm@+_(c&Ftm#*LO>TQe2=Or0u&IUS73AJN9z`(OpS9Hlx42{(9Qs%5#Bs*y1dz2~BHz1WIw7VMh@!!`*3p^2g5F?2nJrD$T23LvYL0?=p#-N7G7|&xd5V^yCtvn|{Ob2ccIPD{FgwKIIQ@hyR-!YHX_251&7KcJuhv&wsjk@#^Wbr~h`V7~t`U=a8#w$qH2!1|=SIIZ*3Ek2lM->>3lfSmrA%<;Q0?l+gQSUy@y;u=I_eeyG>|p++k1!tR~Q96^CIBmuz2*PfMM;5Y4Dj_W)k25&L}-0vU{o0I36DGGQabON6k4*x4}{mvl5v_aZDsM%9y=ht*j3LdIEtnBca9M~oy>kPQKb~6$}DF*`TkLnaj+B?x2@IKgYk8vmczT}3mZep6axY5E`0~Rnz+sZD8$5({efov8W9?dvl!2vwN-uF-6ynOZI(VK5?UcC702fX~Za<Y~KLV{iTyT=)_KmWq<K7Lw%&KHhk>s-I;5x?rRzW^pXb#FL7peb%hI$$Z&@0D&ueqvhl*cs+Xev5)l#G9;VV+fo(AS;enJtfFhw1kHX&DjYIyr-24H>DTjtFb2uvd)uF9$3K{BX?=D^J8+WVT^VU8zI%s*tQ)rqRk!O=X%I)(P@$N0y{#^cX^52Fn7vMIkxF}>pyww<jwJqvy0h_#O)XM!#sT~R0S(Y8)q{#_2e<W|DdvuUi_t&0c1>rmLpDWwqBtR<)V!6HTbw<k`yiO2_)zY`Oa9&z4x13*Al33m_b!eyB|kz1MyvI63fAeiOris6x)GaU*t--fy>-o`aB|DEUP%AU*zVvkDZPL%Wu5Cixr|j8!42jqzkE^v*Fj-`}$&3A?=^F5f*llyihm|vn|(kRe+j#VCo!bIae45H{O&wSmJpp^OgK7YgGlUbwbjleg#Q;!L-fY^JGju&hFsej=$SaQ#<DLT=lfVwg_>XrCgQHnVGOIjuLK<)PVjbsS^egGJE>A@f$Jf+QV|sX}4@85kLWha6l^SxX$mXf?b~vQF;(s!0I6%1TXx`PwkS-F6|*^X<=<udQ1hq66u3!1c^#Ef?Up6rgR^uPo?9%>N^NLvC1jZ%MeBUeLe(vWD|}PW|`XQF&j?IHigQ+R}xLDJ+-QHMURVg!g}D77teo;RU&sJcN_5e^Y{O~Efd7kW2+N<cSt^g(}HG3fDR9YLh3KP!)g1+MH5l<vUNbcJ#bUF;!D!tYxjIWDo3Yfc$Au59-m?TUsYGdsqAV?)rxmH4ik>o$Nlu~Jj;Eq%BOgX`2KGN6uN!GgF&Bn5p*fN7jJtQ`MLJ`a0c8zbF_}`qA!pIc}vW@PSSu}2(0nZT!KlwjE7)^%xhRpwtpBJv^Ehb)j*J{Fp3yrMf0Nrr~@gI{z2JcDz3phQjS;Xb~Mxw&N4P(HharHiiC%b0#o|eSwWHM#6)dHtL8c8lqZ$E0EaPFbV_K&NY}xm3)FjR>mgZ>6`DL*a{bpZy%Ip#bh1RORMDP1*bsSq<8+wZePlmJpElH*fVg4?;cn3)x@W^GiRK)AUq+3A(|zmL1ost=Xj85yPyaO<T4Mw_)4X#>vJ|`ZYm7ymL+bk#Z+1UHvxG@qsE?sq2iC;x#~3mWd%E#sBNNcz66{F0Q4=V@bn0=-D5FE@Xoi3)*vg{dWYk4P<aZxVg-xg?#7;@ER^5F(z=;wSv+{Fz_9iiK+-mCcu&N)W_$>3|Xn+QBxMRq1tuAV%RJN@x<U()nj}JI8AfNw2$N9+_YrKuLVV|@P<WVlEbvfebpvUoh=e2T)LpSog0bI?)umqjy-OIPNfneWLFp&Zx$BhXD9j8IOJn+=Cz3x|zfyo#)Qrd!UBAJ-Fzy^Y|lTe^@QRT}@E13DtgP%0dQ6odg0G+*7XP*KZUf9jX=(Px#Enp?(iB{UD%e6GFNwZ(t=;L;mBvunFfUvz-=Kdev>OjT$w16Wo!pdIRx{iy!7>rUSESjuV&wUpo+L*~{<!lobNle5P6<!JtgEZv|rTys27*U0P(kMd?^eflj<snaSscd#qP%GqDI$y1q0SSi!o??z^fhKJVt#xOjjy-F(kiDIJNpBd1w32d&may~iedLD@Dw}G=be;{-{yZpOkyc}W7d;juX7<bohA^xUM#!EBuA`Wo|DivYx>?+r_3xiP`?Kr5@hQhl#~=b+5!sO|c6f;h0w)U;>m`x9y`oL&f?^2QlPyLvZp#b3L*unvq!{^nOwT*oOm~#NZ$3PHBf@^r&`%T3xH5?4GEQzA28U~3H77+kjeMO=w;xF%m8BX=QT82ESK=S8s8bnx{rN95#;=%VD~fdy>;xwV86|2|g$b;R%e18%%iY35G%G~7%IwGuBe-iK%p@`7Im&`08q*{1Rq7J17T%WOubart79-xx7zlub6;H;?DoCn@&R@=j&a9ZG!xP*~lV6-v$r4OeAaRqk_MXEsS(boW;ZZ_j(n)9i;}DNQ0&EX|5fyc=8nU02BFM8r*s;?i7ClXCL*g;E3(Erq9&m~HKKfc8arTe~vpKOAg=V|?&WmgD0vm&{n<i_=--TbOlyH6tlEqSWxkUm6v2sxHsguBD@sG~BI<-d<!F3FqA`oofZ#xM=88yxGp7|=>6X#1G4{Hx8(D|JqV7mIwP=0hvk`qcFSw5-6%85f0Fj`@0L<t~r4-8afvTwu-52hzUNf(__3plO0;uIufoE!_vPjBaM*@Z!k+sq9jF2*c!^aih$bF=lE2`ehB5GM^Z0L)YHNj$u-l*S6=Afcm)d9)!E0|Dvy=rI_de(g&-b8#7}i!i#%+F+2ZDVtt~w9bFx30?;aO)HdLFq9ljfe^A9100Y;pFEQ(955PjQ6YF_0@YkJur^fbc!a5u2tbphNK={f6qvjg0VY!KK0wDHwoiu1$~41~E$q1(DMmm{fVf=YX;mpNq1NWyOFS;MUbk5wNd<LBuO)o}AYL(QMc;A2mK^XGov&!ol%zXcABmFYO|vB)&UsXThRBT*fDUa#l}9P3RA^lLIOwkYRrvHu_$reH&EZU6*Z@cjrjJ2QQ?PWqzC*5L++OOm)B21hRe55gMtRI(vnM+iOl1l3{27Kr)rKI=uyrQdI2$%GNb(Vq%Xo%Q>8*fzwCxsO*9p?*q*i~IOYORnn7Vwj88MBP{+~L$SCcWq`?0NVSTurJ+n{A`CA#1K?ZIvNBKvaRRcVv~K>#A<coI|4As7om6mqUu-^E_`ol+K)=sh>E3dKTI+^87osyGG<qe2v~Fs<5goxYZ+7Q&JLfBEI%Y!`zKHV?zZc|RGiqZEJa?4#mUNdY-LXKYrhN@!o@RnAyU;r0O-g;{0TPxV6%<%k1{*{0)}5Y>Zv>0@}Kwa*X~kqt%q>Wh-iAq6Z{Q_Qp#dK+yi4BY}cMz9eDIP$SD1=5wROJi~0S?a+Ok1OzFm&fR{Ljkn}9nt)XRVy1}nFkLxonY&2-w%gaF^1*~jNP*=T6=QBJjPXLxIsCSV1Nmm+$g^yC4^>b2%DD*<hF+ni{IZ<1fwGC!^;TNvE-7OSP2B5ta^DgM%HOTft{xJRD!M$s1Ir;YMy8>ak00z(d|DCfH2NyITv6>hlyg=A6u@!|B1<LX>?kveEg)z|3cADTzq$(+-SM8MdH!<o%Y?l=tRChXU~g;7s^+lq4KVom0zxywA)E7h0kveZ~gUDPHdc~AqqL#xjxe>ow<ba-fz#Qn_1-ClXCK?&|yJk3X|k&XAmkwTcl%mhCq+YOFjAnz*M7z>iP+A!aOH+1r;RcBaVN&ijV@<2<_aOC0)~-BS<c^uHTq%8nTc4(xTMuk7+x`1(&Qe+FQsBgHf9~-@nnx3G2UIE1&JYzZvr>?m5Nr^fy7mzg2jvVtIVVCu(1qNBL@^Q&+y);U+m4E81|RxoOKc5H~EPFF;>jSLw=Z$lP%d-@+cbHLY$E*SZ{x1}$)|Qc#NF^dHUZYjr+ZW)<vPPlriP_j*f1Y?<|H{Da2MJMdX4wS81v#qy{I3Sv8nbf`*(FVED{rg7M-n3<V(S8Yr?%()!%KqR_iHAgkq#XQkGA%h{Rs=jYWBXUcc9{xJ<@QBcp7fqdtgr)+;-wA2G#Ew5Yu(xQhN_#h;{vS5Z^l{w_gQJH3Ybp=OG~1m@QQOFRt{98R+9v($r`HlZL<(-1x?b5LG_eyWd`gNrc55KQ?ewB8vE9q4hrVLQW2SG2JMWi~7G&mkJA|5Q_erB;`qY+Dj!?yavu*1KJvlZB{brbg#?~fC;S^N#N#U5s3Mt@1x8uGBpih$UU9R(vzi;CPDis`}1fBSMir>v4oTQ;g|F(8YJv^xWL21a6R2tgnWn40iy`rkjb_Ci5ywm<&VKW(Cfx-CH%F^FowE9u+O2xIkxLymlTH2gFbO>j1t`(YWUKf5;*ucSuKZ^kh61Skb$~G3r_$|XzqJw3gu~o_QMs`#H)!fvqaM@ze9%epEr3v+<jZw?D@;d6>prlx!BU~A;l}E!tYFkhu@8a{)zC^LbDgptM?fQgBzg1ujV)3znUObz2w!run+!?91MyYLv-H756lJpyi?LKY_XVd4ch&-pIyQ!lU*npb_FJafgaoY^Wtu8;~v&2;od=q&7X#qo|N|3G(^7tvfJiS0BS&<}9gY|lUwje?uqy8Zhi*}UGjz0|T&Cn7#61sWOb`6fG+s^dJyjH5*%;@J#UJv4EPiQJv$?s{U_{B6-lEJ~=Dl~v#W^E$CA^Zt*qr!3Uqgvr{9%>pWNr9e+x7AcX?>?gd$pRQx22Qf5fUmGa7j$VsQTr4G)D<J@DnKJEicoZ-M{pRFIS~DAJ$1`rjId{Uh074>>|y%}wn-@vrP>_K2H#}+LxLWvp9ya&VHl^DD>7HQI!59fs?x&LHkFi5S440yf^<ZD>O|V@wI0YTXBO}_B>f;27N2xtPM8dcM2sh2iSwcOZUvf8;GP30pynuSfo6y>)E3&in08L)&L}d)O@<m~R8<&M9aLGqNpvPRL3agKx*-_NKtvMGris`~B}yJq{YefSNJZRJ!AW*7$$a1v3}U(%{KI$>v>2jq!ND@zzXb=zDtn091rH-VsHkjX0gulobqvAb$0h=%dgd4PTHK(@rv<m&{-z6BI=9vyfxVEPbIod(72Op|buVI#mo-tyhga!j0HqhUX~#ATI`As<J^L{&NmOt_a~gvfs%WGT_%D^)Ta%PjwBB7T-PP7oe+X6|kujU_KEO#-T(mL8ILfuq7h-|tlFMUc=lhKo5+yMkr|Ga>_x+MLc1*M$aLrSJQ0OIkDT9wg<k?5dUaQJkB0~{+<UJcIP0}j5=#Nyl$`d?7;jbTaUqGwGNEcsktTUct!DK6ehAU#d-)T>EBwR&D=~HdvRK!^2V;R&<(RgqlJ<lK%21^=EGp%N&+31~JH0vx3|H4IIg*e-}B6Ktb6`7)|LH6$AQrx>|3{X$SO1cMAVIF<WTw{m*8aI+ieq^BxUpr8OXFSJ3lh0UFvzEWJvOva*)$;-w^x{%pO%h3q{S|Qc=Q)ESoGMd7?3Q^Ydp|kKbv^Y^w!*s0HrY#u-wyq7YPxR4$#<a3HD9lsZ-^2#zEHS4k<6{!UlJ9w2t0v<%yGz#O{|z)!TA}Lb?BZC(_vYqTt~5lDtL)ZNW&7W-QogX%ABd#b``2IDkZ}{{mj_L(WbFdv8VmiH%)@JDho4IahS<@5Zhc7aiB(XPxN#$3Cp%G;pT-Vp}{IaSr!wkPbL$Kn_vIn6)5eNvcCp)t(>|&q{3B{M1nE>05-=*lMK)%LPxb5K88_3S8Q<yK#kqEI%YdWvi=yw0(VF?;dNkUg6_!57lhkwV}19fK?T5>=hTiJ;~|gLh|%J%Rgx1BJgB6UD;f%uRm|H#8^;$R6M<S#^Oo8tu^X%u_xOxYj@x{mx~qk}i?mngOi7injcLVESRyrSZpEE2`=sQk%l`B<;VG4?7S%Wtq>EH-5fUnKwe5jlqZmr}iV*$t^s$FdSN=0GFPmFZ>Osk?bGb=g;VrWJ#B8({RIo<{P^GG_yk!N)*%!&U%O)xcgSaNInhHVWFf>YfN<=Gng^s9_z>;@}krgT+Au%Vcv)3``Al*`8o_DG$o=P`axl^ccYsu4(61<e8%nW0AoxthVFt~pd=cR0vVGn7Vs)%j(@nRIN)3KM4se`or%0pG_nU`M5)q@iEpr=87aY<=~Pa^wZfh;q9il&`ZFjFkoJ-6{-$c-i|Z`!uYRA2KVv4}8ylsVWQ<LoN{fO-v&MHX&YZs}3UB~!I!n$b4nQtAZt1Pu|r{#a~nS4FK<j`arzTx323;I}a2B-cwg6t?+D*wDg|OfF39L`WVqZ~3qw3lEMyt<MN~n?@k1-8+7Lno(mK0%R2Lt(QxURc4-TrrS3qqQ@+)KfK+$D2Lv-bxe&bE;QygaRb&|W!9P|O<%%#{046;l8~W91<l`zeOF0JYoN*JkcqFW)axABP`zH&^``>ttbmFZI~9nZCA=dKqj&o?M>uqbTnb^v`HRk_S_!a`!`JwMa7)}C!{M^uJbV7b2UA~e{aJ7bdvrG6IrGR3ZXqANjCN|!*;L)c<5M^qi<Ubx0edM;0*h`MVdxn;<O?a6{Tv4q(N^?G!$0nr`XEl!nA{P(Qvr<634IU|n*+8EbK)QizaMQ{wP9lwDfABZ<g^WV)d5yBE*cA>v75!@P{GJj6*~5)Hq&<P-$g@h{8}R`c~pi|Q>q){FG~vVQtY^6a)SCFM@uE|KP<1Zbk!&c@wLo$4}(Mm38qk~70>cKFiDk+v3FVAtyAedzjdlypauv3RCsa2P$OTmtg$95juM~Zhz|H$lzNgGGac8Sbwn&9b|O$auX06$a3I2nglaA=pdjzl7p+X*Wvh@<*aPvqYvYH!qg$DZG)#0LK*!Lo8H5N~@vn&DKqmYkukoyh=38RIX_e}6>_NO0JmIJeX*u*5_ULnAKl$T@Qe=0mVxZ`yN67aZmisN*w~qZdfy64J^DOG>rHCrExR0N|xez7!X#F&I)txRK89qfCGH?xC&n%jh#1t2kF~@1G>dYj)B%^&$m7Xb#e~!)=KA<XH7Ssll<Z!-y;wmkjf|&*O9JS8LlYU?&iG@*oBND4oKw$Ovj#o2b1d90tTVDEWwR%+fxBx9$f!0<=Ap%D`r4$+9T4xUeS>ulP>4bOx^1{6n(Mv+jyY99}Rd5`+$iMY>*Gwu1PXOH^BIi^SuRPL1$9z$Q^zG}X&z}7J&Ifz-I;92{Dj@Sop@tUi76uFNp7Ho*bkriPFj99ptbJLVi89)|m$B{2Pv(dZph4?=dCU?8zIm#1JM{h7?kPBe&p`etkIrc_a-L7oNCXedf(28UqH%!AMp8N%hUnF0(+m#TxlANk5sr9|%%r<zBAx=AwSmgO;z>k895>dzueJ`to}>1O6>3JLlH1xB%Hj>i;dF9WvvO5zAR-EM<>6Di37!T;-^g<-uR+-WNt#T1;M7>IR9z+k$DHAr=f20TqWjHqupP8xdbrzzTPt*hLSvVGdQH;fb?=o-FL<0Ti!S3fjZ?EixU(v4GBB;NT}45zU<BxKaYkS%O-F!Wr2PgRP(<)kTtF_vYBPuws4CJjhfM{2Px7j1#Sd{162>EI2rqehChjYP1JS6?#j>WhCwH5L6mpbycWW)Dwjj%|bUOob*JB6TR1mZ8eq1#eRmn*&Os~fY{SXV{BhE5Eor`^R8$082ul|j~TLBXFYuSYINylG;2i~qnp_yt}Dt8sDe$tQVxVRWsxBgh3uQGTfc%xi$_R;DY%^7R?jR=348LLedi;mR%_6R>P?`$k_Qpqzb4_iF}R&09|W>zll#k#_VKtV}G2eLSLKaPw3o#oi(x>)E<#&`gE@25X@)X?qcE`}9{%#ne-1KkMeZZ^W7<LGRk7C;EAZnW!{hQ=KlmqQE>N4=;*48e218n$E}OIWoQVv8)hH&6JH`QLo-0$79X3_0Q%SrZI}22~Iclil-4FX+>Vhx)e!peQ5l!UzUhjAx>PLHM7Z6XxNR0>}i2t2O~8fUG?Czv5U6Dt$4)KC|P&K$kf!Q3$Adxd~7v%zjr0AD^bQ&?w-Im@Z;k(cT?3{wO+C3T!f#a~3|2QU|nI`G-p0ii~VIibwKE4t)@fMkIw*Aqf5v)WqA;RTw1(CrZ^Ksw%I5Z<^6V1-TEl5yjhun`4gO7dSdLJ&l%*&&G@N3hXXX;UjvXF0wMXj*)hvX{}tTYUJnKnnclP!`z3ZYaht?OmvS>#@w($Lr-@z50%q#RGB$%L?#~5^K(NpX;-V62$3qXt14BjH)V#>Evg{leW7}E)EN4wHP`Kc0^QPQmK@6*EeslG5gj9hcL8&?3c{fa6k3;!a}Efl%T33r2*>Hv(WGT;U5^d>r<AyXG)4UW^e@H45F*dJB;@oV92M=}9845!g(Jh$iZRDWeMTIW1QY+QGw`W$Mhg^uFdhii3P*B7Fow^|{W@(VgvS=26Y7^$x=^S7Fo-zp=Ec#Yu2+EQUnk1HPy7=#+BOCgIrcg;$PusKdQP20xo!(zPP+~ffTECyT#p>jKG?Vg#8g&&NW7%Lk%L1gFPI=NJT^5(Z%XCacDAxsYKk=o<H|od@bkC~Zf69!>Cwj&ZK8s6zzi-Ujk?PcLyIfg=y69hrzdg+bmMuM(R(K`!n;(|+!PtS)haxji^(5pS2!)vd%L;7&&)7$r=T_nLec`J&gKRa%kiZ~y>|6w>I!5D!6M{25gt=EAP*yZ?fCLShLce`*2Nt5G+ld45poEF8z~+Q(6Grkbx@3^IrcBNw!i9QAXpk!UHWM08dgf@fY7ocY+VDeBWY*15mC1w669qQZ);4S6b@Y-GLTLXg$|Z8-^w{v2HAXZe}-r#M~IS~jU3++IFLIB(b_}UBcd8>DqWvpHsHF&Q26s)L;C)c2|jmda;J*94F8EZaSznFG#+MMB*^C9^yqGiH(ngA&5F@Pw!&}|KVOY^MJE@*R_pus3XX6yG$~z;S$BmpCk0C84roLDr3_0&+Hx7_s9JsTC!9E<QZIG3j2W~NgAWg9%h47t12*uS#v{AHE|I8!jdmQfHea(uY8liDYp1eX72A*zphQwa$y?QY#NXhfNaw@LWH)pf^L=T6R4zxxa)%QuV{2G|N~@hF?h)1Lqh%Z^a{ba`p32>>J|rPR%O&h53HlrGwp^KH%)3W<CXlW<O;aF>(P}tM3jA)=s|nHv>oNkRs3r3EfY?Ry9|~|LS#=7@MYHT=e^`Bc+kbz`##K{+oy&U}92ZaENN&Y}OoIt+oV9L(btcXmMUBmi)&oVoZE_PYZ{g<C9O%JKXGAnPDr5klxiBt>w0HdiSEJ@-$O7!rPIO^8&1)pwVa|LSiFaaeX<F6EpPy@dWnsm6HR|;%R2O1v>$_Z?da?^MZ6iW~asygUNJNQOCGfRM{Y0gv&uahH>Yn8<$Hp#qAg#~YPOHGP7iVZ~f~FIF-8NkIda?(*g!_g5hKReQ=Q0-=C=4=pC?&(fVN)o)@qA>Nw_>Vs5}+N8J%>GV`g@Bt^<gmVYJQ&9UqIEsP32WYhD&_QK6GzNEYab1Xq+@PHd{A?9L3%fkfOvb{Z>&LWuF-F;Uo=iCY0A;EBnh9V*-j&OGpRk*pbgMYOx|kTcAieREJ9Sq?8dqt!ih}*V{qk`~o#6a|MgbRIzqKz_|Y~!uKitsEVXY){hNuj#+eT<P^xFNq%V3R6JBo>X6rvgWtMROfa!SPFb7qD)4UO!XGZB#f1Z7NJUV^f&1uvny|*j+2IUfZDM4KkI4Yj?c9%+`ppR*T+T*AnCtY%Xg;0bSwxc6p&iBILO&BN+CCnq$7D8S{(lqw-a7yo&gtvwsCE6J=-;zDwKOd)`^QmP;)CIrUPxZ4Hl)e)8mgZ^dM3tfg<W92wKJ-sbB40_G9;DsCOj0PQRz-p-nh}LtK3N<JyTI^Ii=N-k3t|$bm&iAT;E5Z5+3;RZ_Z7I?y9XT;xT%csff)7_qIofaf@0tNj<F)_R<Jnj1!3pnoLSg1`8B--vX_TLVzg2S%Il1u<mtwjq#RL+PuazFKT`poR}XW!UjGf3)xjEvtsuMa8q$x^x<O^thcXj679x?2I1H>@2S9s4D3qX$WVq_u#B<a&gR2Xo0a&1k$NO$G!#?h{3=%~$aLx(Hp%l6(@Fv`t8U22D+!tl7Hi?HmY|por4o@og?;&8*}t=LW@Ik&vOcHkIETpgoxs@J^jQnXTT1WF0P~Va8eCrgMQxDs_3|<(xyaqo<!K6gbWr>`bD!QN+W#uv>K&|QX*>KC#G)zpNih+O+krFm<bL{)6{QY38jeC0Ghi0OD+xOvXbl_@+-)&zA`mKFkibZ(P^QMcHXB4oE~Lh06sIhAWE;{hRO{3VBVESwDh)x0M-d0I@5R6{#i#op8PSDXRN0Z7i~XodvS#=lo|1R{wZb#fPO{oIwh5ILGvXM1tDsL=z?62-=M~7Ju6=XUv0=$^I7ZQ&xBn6RVmz)?X5_To_p;CO<P8efg}Fsp7GT8C*Q|DoQRFJxa8~EvD#R%A${E2UQG~n;j@N6&ye?#OxQQ*O4g(sf-8Se_LKPZVx|0gxGEpg`^880W7{rr>=(n7!SLk?9Bg1>)l=v6gn+tR1Q_=&_k|WjHn)NFAr#$E!KdDUy*l;e>?m#NTG|p8uuZKqzXCVuNKDDnV5DAR<Xc*@&M^r)0#nDNlO1d+uwapz)i3SL<_6HV~!3qz!;)lj3Qh7tTCB!22;WWI?kMCnIy`;PVoTdteM#)jCi=slD(<N}4t7aXBpUk^WPsvO1xMMa*rp0O-K`!W+h02an6z+V7^lU>UM3qL2Cp1AhZh$=eHUn=JAVy=P7X8ZFRMv4NMkuzqsI2SvHJy_y?jf5CO>(mqVrB;!Ag`9I`d$8nhO+X$p%*F$AQrzE7D7784^mYQlvXZh`iRY57_DTC8K@YSQ-7FTG<wzGU(Em+40*F!{K@Ip(SWxDfA4W!l5*}M<OAD*E$}T;;!Xt;N?!(_F)0YTd$S6t^Avl2H_<*{YDLr!$|1EINaw#87s*m=Zbb-O2UP{}_8)KmA4w&M!v')).decode("utf-8"))

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
