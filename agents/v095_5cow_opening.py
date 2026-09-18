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
    'c%1E>U2mL6j)nh9;OksOvg0Isr#PC8F-~mA$^_XU2m<UZ7Ff()WcO|{|9x#s>V7{C`5dyUrF`hh?e12;EEcPZJUnFm_<v9S<CkCm@%LY!{L4o_K6!KT_U)6OKK|&*fBy2{|NcMk-+KR_fBf?6fBpS`-~aE&CtrT|!_ODrzWnCm)suIhym<ZnyMI1?_oeM8Z@<30eDm(b+2OOdmzQ6?|K$6xFE6g&fAab6qi-%>z5aIfM{llPfA!sq>*e1)|M210FRw12*sp&2=f@wd2Kwc9FJFE2^Sj|*e|PiE<A{HJ^8Mx8>zlt;ufBbKb^Z17&8>>?;dj5KpSk$`H!olO^}9DmMc?UVBfF3(lCG<W#RKrAmfDi$@?x)<e7J93UA(xwdzL4kC5f7&JL#6Mj)PrW{5!e6y*}EsEjEaC_z5kS(AB~oF0L=Ho~)(2SybA>M=VF%z}wf~MP|AYaILD9tc{5~K4KxkVG3?0&d`he^hV~+wC!ymTRF}Q9zV8heE%D~Bc%%33DB9pyWc=rY<u1bIAlWmX|pFN7PF%i^=k|J)@Q<u8B*#w{_b*-yECLd^>!hxnOip|T2aT(LBjn3LQ87rK&_s39Pm-XqAWuKELXCSz>;N10I}z#a_l4;dwTQL<3s;^4?S!gcX7x0N`&>F562_)xab?fHvi)Ft5=sVu7Cc^<<<4eS1<pq<QDwpeKZyxe~pmHbBE;59bMb%Gt?;V-isBqcuMpY_5Rp+UtHW-$MMzT6ur^G&~O*=%3&Ey9G~(C)S%=+bn`Jh;h+w^2`t_E;{XrOZEH{*Tnn{){L$0RBUN~@`h)ZNo84~g+pX#C<*Qdh@)`RqDrGB6i0PbQ*S|+S-1mX@_<+X;JU-wz@PI#!ml$r{=X)`82eO6FhL3-?fBfCKUwQnAouQ*AwsU;6OpRw8e@=ot6Gy1#S32s-2lNK0rCmNy1A%?ePg%`z+6bg>XEy+vTfW&xngMJtri>syBqY!q2k2_TFtnz2at_W%9#z0Nthfb2qa~83-kk9a^=g|eqmwiYB~JIqvUhNNz^y{Ihm;I4&Sr!d@aV~LWH1>geWo9?372E~qaPqT9`-JS0M~Ul|LBfqi_GD>osXdAJ%gGh(`pP*d4$r*RztPMr`-4~CYrNN%fp-;pKLReF1^2Zt62`Tpd_n2U7&rC&CcBYv3N~x2>0#I)}A4g?Z`7IvQlV5Ad)vJ9y!ZIb6>{6CyFVi;#<k@PI`h$D?L8oejgxHUnhn!gD|J=Xg-AVnQ&!uH}KWPx3`|hJ$a-P;L&qW#lG)qis$GwkY(7%U3z8(Z_x0RTSu_)h?4*y{Mbs9+YWOWfyr~*__p>B&&Gi4qau#)eSLBDw}Ylu{|UaMjn74Dw6iRpDY?y^pl^74@!j|HWX_`ro#oPrIa<GpCpr^t^~J%!#IDoGcXT@^kshppQGB`=d!d3ZwCw=x%4+w8JQlFOnzV(-Bx)#B4MzN`VV6E_8ZCHkxPuQqI(@tdT%!r-_9}tlaGOC0<>@BdfQob==$S#HRxZ6G<>{qxKb^s)9(n#jK|>Ni<nz#x*F!)5Ap^t1>Ga8sDEh$tU<$+W;_=nQ$kBiQ=5)?88qur3Khc%6H(0AWWuIm`Q0Ggnf^==nI_fJPyt*DPD5Wd~FbgPEd1_+ho3}u6na@|1gu!4;{trwE2nj*UQAbj>%I#9`IYD$cXqA&!jph-?pIa2H%s|eujv=IkZ3Ra52aprUtIWXC9P_z=K<2s|JO7Ua6G=X`K6d<z#<2^csK_X{sl~JIRjQ*}JhsEV3a83VDx?hO``a?o0(nJ*#Q6pYB$LuBOG3eIh_w&|i>DM?wIDG$R`(>~2n|elD5qAYf!e4#YCoqTQG)O&X*fL47Q<E1jEt!i#frs7Co^8Px5d`Dg`Zj=b=W?TYE)z$#CG>7)=BG0+*c10N1yurxC>D!6A5wh;$tAHl_cp9#Y#ET#mfMkYvyYy>{)Q<s?pt?xFh;`IRvQV*|7r~`ynfYCsvACglLp&z1XW+Oeb&`;oU&Bz;;v06Un+zW$|(w{56gg{lhwzOfs}fy$7m1{Q38<U%$G^3r=)OGvTrbiK6D@Pq$%QG@QeDKRhJ{n*F4Dj=GcdyBU*?<|ewc=IUuaj=K-{q0!wZJ3s%EYR-H7m1&ic$b!J@bC>EeCjkAOWN)vpF24Wr^6Kgby_{Oqsv-GyBFyUX=+V_0=Sl;7&cjFOzUWC>;mK>3IDyVvF*^dm{BR%2>|--gOyEFHXF!d$QD?;KEwe%rSCI_`U`0sBO1Lojr+uj!aLKN;G&<!<a78Xij`Wl({T{09&VBWVjL*+EyMpq$YbUQ-{ScU{f`2*-6CXkNX|4lPIE;M`@jwfKqh^}nr;MVjTc^Sr>@>6|a*b*}34_S9u6>L|{_vzyNHR-E=t^>>mF|{FKc)bvT&_H<n9F0~0XewCkBh+(b-LSPDeVbIVzIe~(u7}DV(z@C#!{Cyqci~?=Qa=rQKa83BYZ&y$-x0xHE=TVQW!`2OJ&?A__6KjXoFD}&{s*)gKrqVvg%ucfgLZ%7(k%fV;uO)N#NA;!-vv$JKueL{ra1W>(|;O@(pa{73^o09`<9IJX94IJNs|46Uz;CJKBop9SFvS1t8=U?rGjj-%(}wWpvsnbSO&V>y0u`pD;HA@Ou>Gp(z9pA&4y9*)HElBw{K;0aF4Yv<i|6ID9n#4Qjij<E)FAn&GjBvo{C?)C35sg+U<cP&0C%wCH|nR)pPoa^Jjs_1E`DZ=CTao;Sw0{0&d$yc;Vuc7Zo{NYZxOyYtbG3Y(Gfq-;-9cV?RjmA19D?3cF&8&3NMCEm-RDmhv7WP@!M5DG169Z5f@#%ht2m73u(+O!iH1kIx`-T76qaPs%sh?brqnk;cFS6kNUVEdVAZXH>T-)a}bFGx6dG0$zhnusgwQ?jC!XwxQeNJ*?MufW4fU#k6D?a+tq+llfCzr&XWKG~=1&u)*!=kXXlY1672upBLnf;pBypjHBy(|WKPr<>biO&((@M0b#}KZt#u@EWf9boY5?oCcI5Ezy{D#8C8klG4al>PaB0SOxoAiQjEqSFf*wEeNh3w7C)w3`o?<%}9_L1d0lw@i==o{RVzhz=kU5dI0QVtMoxFXr@;VaS$&6(#Q@s#0;0@A(rDIn!ivFm($I!=3=I0T|REIfOLWmY8lZHgl#f5h&VzJK^EqM#D3f7e&GYH1V#J{4oVn}i*8UeiuRn9Z_EJfAh_XJ_bogON>Yyci5ZFS8XOcOR?|ZT7)m)-caB$Qf#wlhtx05lCP+WgT&R^hg5+}&16YsPu>Ncy{&F4OeDc&U&Eeh-L0&jWrTGLY)i8i`=}%S5_hkojg#Z<h9DfD)ohyS@B4yFFm2`A8<;Ecr2k9M#jism&2rWilur2r)S!34xb}cGrO%zPZ1_l^t)Cmmh>?oKQB8rZ)CZz^cqiSAh`Oj)C#u6l>bbb>C0JkpC#v#7B)w3Mhwl?-zVm;0<)b0w&v<U>A<Ev;5ABH#3lq6=M&Xf2wfYE0kp7+Re!OEI-({wBbFtm{~I27@o=y9v1zJkV|ZWr(7)mHcj6*8FsoH<>{A8=;+HNKJIA9UezeH6ws5m-sZ9>Ro(#K3$c)eIX(0`lwVKc(ITExXkpwd&2P<r9co=ESAU^V$mDuQ@9;&-7V3?NfiaO(_|0L8&H~fB=a?WC9SlHb9fjNCQx4NJ+Z^O-5i5ruIQ%O&u&$eHBOx6p_zD(Q+UO!=rLo+c1hgeB`ThKx7p#lzJ)Uz*iwk+s)8VfrmkOK!LPEprg8UX65Yl*g43a-Ciz@<e6u&w$&@L9e*-b+9)tL3?`Zn5L8~u0y`k21;ZV?s3`ysoXM3Td%3K#$#yfN6DVJV8dd+VE20Y$Rm2$+;9*LRx@`jWygQ-{Tcph+FU9gmU6I(uHY?$}Iq2s^#Y){WFIebG-gy+FM?{Ek$2?9fbpK2g0Nqjv4yjO^MNa1y`+P1><Ly`mF(CxdHbXlOJ)+gfNVh?MJZPahJCZ43Rx#;b4Asa9O6E$W8Yx@t=Flo@NQw{i8n>6{juBlbMVe89#|u)KPxsDNieMdUFY$8#X0mC41I8~CW6&$d;2s(kX*wdCVf={MsqIgx7=rZy4HuSF_UOcbi;9$NJ^4JUu);$&nfQi~hyta%lQRKjU<<?qQWVPTkz_hnNn{7VlLu+KU0!GK807|<lXkQbRdp)ml@z-CK5oKX;|*$>VY;=NvAF4WYOVIX-fQKdAS|T(As>P72kIH(Q!qryEy;nCuDh;Af$CMqDB*J%$`y%CNL3CtjKHj&#$Ds3QyS-~qKNm@hU=8%8htV8?ZxYl;0n-fwu&x{-^NxTJ04|<Qie@_3~fghVJpHiq0&RfWdV^wdzxxP+@1B2{f}^LDwq(~wv<ZC8qHl@s)$tVYCa$}rjOM=6(F#M3b{oTXJ&D*Tv#Bv@<(%!O&;kwpbJzmW)S-BSY+m`i($l;QUf7cxBAk^AO&1|rgB|7TtC(II7$Ah6WDXx3k8<sj5i>u`bJBGpsGI^A2SkB#6$edbAhJjNj4@Ug*jzTVt58veZ5J>06Q%4!KB`UXsWSs?rv-5q2%p{FdY=*5g@BN^$Ao|QM+Pyn~ilq!j$N>+7;bqPU>oCkLv}ZDo@q}9XzH?B(j{Ph>lX<f1%*0Lo|VJ`gMEpcqky&rEHC{s5^8Em28Eueh6ey^bPHwshiVv?UbPGg>B$z(@Y2AUo~IpN<WIq;8OZ92ivl&<(t^}KGjN>h%<l0o6YT!$n&6B)6VtXs`mt?Tph^C?z}OKC%MjxzLQ9KS5Qv`yB*M6YHe2X$ii)!(vi4E=_sg~lE-b|7NSCRi8CrtGd#=1=y^SHzo)AX>`Pz^*|)>x%x8m$6=3cNX_!?o_61k&1M9l3W1@wN#R?0LBK$0z28kuVr7)KSN=Zu545+#A<N_+<*1Qhe0jwOquoG~iHvfSna8nHQ#R*m#oTUZD5%T0=4g@=n7UuE!Ql?}TipB`2>p%v(<op~(XRWP6smoNTpMrCj0x+VOjkh8PDh50Nl&`aAx4+~`YPaKE$h<v08d7$EFgL>AemW#xRy?a0pAu>57LQA;S!XG(;nSOZR3wJ6?wNmcvvoZpAolyWq$K0|pNXJID+<?Gtj1j-5IzZ760r>;=7)CO?c$4QIpol)hg$Rtw}=;vRFo;`kRppnaZ{$vz;w7&DC2r5%^=F_(4sCn`AotPa{7}tYzFL@dPI>-ADqLSO%CI7I|>YetTK|k=1H>6=)tS|YAk3j61Tm_*d(l2N{{i8?adG~#8{o26t(Tx0eiQxS3W7p2-4u4_dQ_i0FY8GrOMUKD-osvN(ie|MjN>~yt41^DfN^pBkWlH2T)U?=~Ac;5K$%p@@gX;O=6MY<k~8`s}jmc1gUncYvV?UnXL}d6$&vU!0pHxgCRM;rY~hUa6M_#8G*QbuD~ADu^Cnl#rPzl96X4f3mVBG;uU~}#A4JiK>72?O2W^XI75oKv^axO0+i?}1UA+Mbk>jZFLb-Pk?axYk?)@s%Bm7o%<5p=VPrf6l0%FP+s$qBF=ldJEQo3f7E_95RMTauQ%H#f4K*{42R(>uB{6#!uA^nG4^gXC=|{s1E>d`M-)psE6X<hQRLKiQ>zmE3-p!gLjfYUS8-Sc_+i9&584E5v16lkQdJK!lt6D;ey4&R&q-#W4t6RKY=vzb5zK(4{7^h#-H2GAPs25wA)gVz3Io;6ff)2clDyLR-RH{F8xvlV_57kaJ?ie9EGgv$7FjjJBm`JF4e?HnSTV7pdLod5GJA0&E5@y2~(zLr^SqMu2bY>(uu=MVPG+$yD<@f4IG;@UZq<+umhpmO9To{}-ak<*<rdHN9F^LQhO^#&F^6Mq&mg-(D5HhT}$$<>lvFf?*Jc_e(V`B-NwXATKY-<qoxxH6@v`}p9e)Hcs0<_if;NY>1ix2zQtmHf?R6>1JgjuQy32v*BW3ew$;w?IDzyY0%3SDz*G^F+pr_d9H`#^V>7`ECEG~8;!I_~Br?D`t$=9T7UNMiz3pD{*Fz);0tNLZ>a1-R<DgvC`zZMbb&+!0}AHNaHU((+c!wM&z#M?64wI&{UtufT4$hWEw(EB(qfedA7rl4B<?096k>p5P9f?ME3nVHCeP7Xnh<n@_Nr8xE>h`j*B3(emlJ+Zl6b0Q$z|*(9L0v?A_6bn{k+z}aDU2q{4{LtrQnh)efKgu=n!5S_?L9qg9!dAyXxZ17U{u9S~AVdNY6oTvhPngfz6TTqCN0Z_+0Ao1%RGn0n0inI4-X58?;3F$vi-;ehP%N8eK-X`W78<K^7tULkvNTs3hyj^^yxTA!S5wJN!1UAQF^;}x4nJ-pvwyubi7EXz<2Jmj?1t0-N6v<A3X*p*<iiJJ<JejsXMK|enC{X<400u~N_yz5#V=K79N<sOW@2R=e;GfpG3aa)w&9ZUvh2qFS*3t?(@*OYcges4l@0@28#H;6V_6ny$1B%>AlFJQE@7~G-Q3X=4`Q=ehrM^VMYlRv<n1I-f(#D!my(y23kwLkP(usq~;K+f%W23uLCEFJH_wBh-D1jk9@JC8CMjL-?tQ;TvlLE<aN`T$-Y)bY-93FMhQ5&XerkH48aK}*qSr+iYdYqZ(t)x<A+)+5FZT<SUYqO<zOaRBU1KwU9L3wSh2sn3{$<`NUq;!av5f^9~nCarjU2sk=zzDf9h=|M59R;p9++{15sRB(k{!B?R<w{z`=Ide;=_osv$3ZXPERkD>SdSn$Fp~-`u%c~&jU~isT<uGfIg%-_uP(m-^788HhbN+WkX*n;^GP`KLt9GeN+Do5=GlVnVRPsHt#oImE0)xPU|B`W8O9JC3a4aA3FEo@=$KPDTfHwCR4XXy=FYM|5Nh;*T&Wxsg2WQ6VP1bVu9OJ`L5M_@uPUD<OP|B4LZTW4xhevWTcteR&q^60woB0zL#nD;8Soij#(g>Fx=7Xq;~%Z=BS0?1rdBXjgfLWYt`ERS=?LUBszISEun3U~tL8Y?j!FS>SmRYfYhYgF#uqM?WxSk}Lqf(8N=p!*CN!~f9oY&1HHRlbVZY)}ZeT&LP)b_#uiBFO3|6!jqlIqh!=2Lzx<Q5tgW?c0hvjjvD&!HILq*RDVl5D{z>$J(R<l(J;*HAMwxNt1dsbEic8>`(QgMta#eI0<@mVr!*E<OL6li+0Z#gGMwC-~bSTXHdplwl1ijAO2P=#njIFBPis6f!RCvFf27z7--Ek^JFBhM+5`FRV)0}6}QzHe0O1l=|*DxW|;S1jWCIow^trgA<3HD?OUssb4W-^DM~vqw`9rduA(7GZk2e*Yv5xPRxcQuO{-?I#795+FGGV*e7Q8us*QwN6itKtealkHe+b$H%Fji|WK|^3-HNNtJKb>W0`>N|EI(><E!9iV5VoGX_?07QD%$sm++4ne=&$6;WdiRr-Gy(l7%FFG#8d98bwjg9_D!_#i0wf>KbpI}SeHtDz&}N&#QJ{8!%Jc4{+BJP$?42J+x0@a8dCSFidBL#f=rJfld9rrF|w4Cs{e@Lbcgf!Q2^YYYUaHk5k<a|$Y{iL$aKtP}(i&EnjE-c*D;WEhx-dmIC5s3w6)KuRadix7bVi_pyK4p}S21U7jj2fo%K`W0lk><V2Dwt44}O+Ig^7?yKLIYGibAZeYAfa`MctP`amN6P26onTqPDq;zrgR(kYDX?t$@U4~aL6LbknyoOHb(f>V<DRWqK8J-S%l~F~O8T9EGh6+h5Q{p?jtkWviIV9#ijg}tA?)&nhb3WYn)Csp6SA8AFJx3IjfQjVh6X3O0FXQ+*?V<tPz{9@{9Lqv*J7ENM}Aef%;i&gB>JqDQK{6wRS(v>M?5RD*^5@etN<JAmQ7Wfg_q<tGROyrpn*j-D-QdJw;vzvfGf3+IZiWD94nxHfK%0aV;yF!zbi=KJ8<@qbz*D=gucy+VGMhxa4gy<4qA7M66j_b)T>bz6jaGAX+R<AX!3#}$VNj96#irgTD14x>RX6TQ!;Kynp~5h6ph6Tjw-=PQSe)8XT`dv`p;U$nU=pq9vOyDsKzUXNHp|%9Q9#u*$2X(Z@)|Y#<9~5=%PBS9ZX-;f+-b0>$vQj<)+=&##)meU}hL&_U8&$rXJ<9jgEuu$Sn>?F76Usn*bC7nBA!-%`thIVJy&wT-GN=k@2vghOV%0Rv8#M3EtoRk<HcJF1mQz5mZ|*(8IIV?X$R|?zTzkpON~sM@j>T=6r@`#y}mpEpp!3{D!Fq_o6!ObNB=)pnw(Aq!@=1I28nSY5ecaN<ZtM`*`cV#8%7fw8TQi&>voOw?7q(Mo~1EJb`aDUe;+1Q@92avPv%kD)nd2k=%`?f{|@O%w5opNSoTC)UO7sdR9qZyrXs9ct)oVi^Ap;uKp^YN4d~8aOv46<((O0MEwPd$dYoD?kZAqqWD?+U@)>e_16(sca@_Z+Vo&T=v1Uh@GJF#U2S7i$9w*EgL6ZN^<lAkaoqgWWWWIRKJRRElGsC&kUL)(((2g$wuH+vCbRuPqVA*MO5NO5BwO|~*8>!#fIt?Ck^*17O>2Jx!XmRjx>5*t*G5M!oxhXmyWg|kM|qi|`qZ9bKXf--w`7v24otsXo<Qj-3HzG{PAp)g;8_zMOx#8#FTnI;uJhvX*q_SrmS!tEwL-aH7qe`1d??=u{$@8bj=`7HgObjZv(#+4y&!lTFuQqJPC_%T>x=jLPMh=J34rDqReks+MQn*{`K^8#&2#-Z(<++OF2P}g;ut`_G*bt~A134N@7uWh#Jw|&N)PECB#Clu`5fV~Go$oSzDd08Q`W9k>I)eH6ktRF>a>7ZY8G7ufCLR>F&`+icb`)8IPG?wRyZDxA4U>zUGA-d5(zH3OA#UQW<QWDPDbD>F9Spex+tsMImtEGf^&Fm0Oa~9gP1r)R>mcF;CXUq4ma<zh%)qfU4|1@f3ygI!_Hvo&kqIh%HuB>8<vd`w<{Z`HKxW@Uj@`oMKT1cKrmMC{v%V9P!kjt3MHV6b$kQp6IbW<(pP{44qK1AHIZ{34*PI+Xj7xjdQQn7Ku$pc3+zxaIzrEEj7B|T%3YmEv2EjR1sFCgh9@R(jHz_@PQQU9q(%}na4otnIqmJ4>@T{a;?*3UoKq?)*SG2&u&mEkZ|4P-*~NU11(hc+s8j}2y0z*g)s>%(R99kpx<UeldI57hCX++?Pzps<c%t8lwbhxpd_jaTAre+jz@!pNU9}*vBn3}t8DtA}BWj&I5z3I9nqlmXWt8m+>q^_A)JLc4WTdNCfth=(mQLTb%9UNUV!;;2#z0c6SPR_xq^5E6v<~U^)bk+X4D^nXc1AA;YxmsKq(H_XhdS7}t*9hFJc!z)%m+c9-Cu!-GTbONP@^|Xg)7#wq!1~MHK-_sptC^>rrI8>{}12mgAS8rzm+~=fCkgrB)E0xDm9{cn6IqLv9ai1?HFUy!}ce8I{K8mM&WGKi)~Eda87ls23ua`bbkajN}QoaMLQ7L!X{$r_8E^4RGc&7NW$zgM2>US4{cbZm2}#~LPF<yzBQh7l;YFX`v%U`>9qccGu;>eX(Fz4=5EXGt|qBA{vaI$z=xDt%qFAdqw$B0<n_R9eN>l<ZEpJ9jDg-q2)G1d1I{$1AYEC2`nZA`>2t;kWJ>g;e4i<`)ru<vca8h{f$l)*X9e({+VVa+rW1U)Q^|y>Xyvf1f#HNfQ6EI1*9{ewH&ZG1I~7QZ!DUeyn^h2(FCa>;S6YW7^%RL5&8d(^Qc0Gy$bW^<%D=%0F$~%LGmN+pK(&yMGz6^G<a4Z@gyx3N+9r|dGe8~TKn2~$fzPcU=t0>g?@!gR5v7cCxB&p09~O)7xSC|7bb?&G(iLW?aS)B|)fX1(@O7iCr}5urE4DjI<m#Ac@oq}C&Ct%m;cr%11>z0RjK(dmz=0rtMtIG6lQ+l)ZxN_%OTzbWy1PjesV8p^l!IlaZu7R`vcd=>Tf<?8AOB?awqj!iYwLrZjv-1pBv7e>E0S}bH>6L-F&_xjY49UG<$+q3X*XtTQ)l8DQ+38e<K;AcK$L+2(<oLVgDax29ED$`KwL-Tc}MT8M!?ap;to!NImK8MCrGI?_3yGhrE;O;oare6UJj&{C!L2|!kum@0c*wTz1BD@q~&yGQpNyk+0&XDC_R-iLoHF_-aYL%hBwCq`-@Lz>r7sy1-j8m9C`qT<sPFm1*K47DMzU)6Ud(?BhHwm(Cbv~K7E!8A_b+p@%;9?<{T3Aj9>zMm0O9@WG>8TWER~*Hv`293y9UN7zN5^sjEgdRv&|)(put3BKTFh8>%v&`g#VlG}CYNM6E4+Ztk?%ZIo=X?dmyquBPQ~1Opz8MK0UOze)qF<Zm|kOSnnnQwK)t+gD1mdY&i=vpxQ#R#vNTvp#NEXc_=4jSwarj5`qEC1L}15m4~&;yRGd(hLfcbpl5Ug-1qSl(l(AWy{%I<xz2OM?ulE;Kt9VYry&N>yl8ozTjXDl_nUq50zSp%-|T`9fY+#vWtZlh0lS-kHe|{?Y)os?qYOU{-`^X2{a5i#h9`fja@VqMyE9Uz>YpMRa|49n!N%{RYmFp14ILv31=%Xm9s9#Z%DDEw;-Y6)V@25$hcV)LC$sLo3hM`T+U?T!@({eT!HIS+KbvD2tU?!GVS`}8UhrmV+NhUsh2KQ=R&P9miCoq8p~XK)XpgoPMBEnaN2=p49QhFT55X=+$Z%Dv(G~+d+1*&>)(Na%#x`vY-zp4V1dykNm;qohU;W_9vkJBGqmG&%fu!v^2v!TpPH54gs7ldEPsR|f?a?{u)xd%L>;Wml`^}cR`|PcdalFN8HSxzd4vXvSP7!m1G{kmn)nya2H0o5dWX9No+76b;m>M>#PZvXn3=?RrEGw>Orz@fdzlWxY!}%bX25%NmU7J<1`3nf){MA1xYSQC@G^8?ZFT`PF%^QYmabd5ei{s34lY_yWS$C)fSj2<z8xv|-Z0!XRh5{nPuF*5tfpG7sGFY|1U>WG{=BsKw@zY}fh{At4^LZl%H+Fntx-*l2Q7r?Gl@dVJ|$qe4A{hWDB(chwU)ZywVAC^E~~^S1IKnhIRjGy4ez9;eWxYwCV5f<t42}-C<fCW1)B1y7feorHt-strDhO^F;%P6@J5@TmrK{A1xlAOkQPA08+{E-Or=)?R?)Xex_)z#IqM0I2_h^K$-&2vCgvwfsTp7~036s^O0)V(7RtEOoPnOlfmMY44*U(;E{Vx@k<OeH0a&;!i-wUC_-3yewl}8`T@KXZiBh_xGhcaUniyd_Pu7o>8ltedN}RD=xv0&WF4>6cUK~Us7_Tu!OON58>{>&10ZuuoHgL2x*4%{GMxmyb|6S=)9hr(dUI#Z6^E$g{HN+u#1Z?9_{mF&?>5Cw@bPbt-1gK>^z|;1vl!7kZ0x}*5;Hrx|ZU=VL`$i1U*Cf%~jc`o`U8mD-PNaK+4CD8F9oNN81ZTw12euZQ;2#hqY{mO|dHfXSZ`&6A=0g-uZ%26ol^3F6k~_JFWkBntT5y6iNpSC?md-RN{}3qvIhIyfE)O>iMqO}W9J7kJ{Mjgg6HIE_+1$W{a4Vk*OOeMDqiVBuCAs8E0rzH5mfhXgnxIO4@t%!wEnapegBoH<(f!_720%2PC@L+7Xn!ho@pUY70JsA}hmpx^Kn4hNk2c64)VGouCJxyU4p-@YVbrl=^2H&sByWz)lNe@rfG5%MZp?A*G7Nd^NJjH__<=8O9_<|b$|y_th6Y|aRTB*x*8%Jy8zqbvO4yqTm;LN9kMqq0j}6&k2F92z6g~$Bu~Q$Sz8vk?N%PCy`;kWa)x#05ootmS-_Vn?rO0O9T)cg|(%r;eK`Y_#Ktmn8Z(wQpLIv(nH!2FQ7#@N+P|IiMQq7y*nJ2;vkFV-wVCY{=?m@Ln5QqIUR_BY(as<}X@pRNK$dN}@uN6tL8qsL-H|HMd7|E<;?PxJ>T$Gb*WSF#jGnD8al^3j+YSA25kfZDE1FYk?mqdy{Qw2%7U{z^~_G@*rLLx7R5SRg_=rb9)M#0%Txx%$Zgvx0^m4J2|i#3hQ;){6r&q<XS6%z7|4I+ZG*#l;e(@JlSq&^U*T6TpmhXEBTRjphZjp^hnuO#g6*J@h;(HH6W`(`WwM?<Hu&$_XEIaZPKX8XVw*1k0xvelZ(s9|UdaiQsaEtih6<p2*c>|#m|@A*m&<3-^(-u-?Qz5evipZ*_4DUE;')).decode("utf-8"))

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
