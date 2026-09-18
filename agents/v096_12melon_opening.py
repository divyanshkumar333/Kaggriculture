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
    'c%1EB!ERhha{QHn&T}xuku>8QN8+x8<qQQ<valWqg8_C81IGF=_Ra9WTT-+8y{Z?P5s_7o<a%{dtJ&SJvMMVpGcq#km;ZV4Z@>Nix4-`W<e$I!<;jol-(0==_3g#&yZ1MjPd<M8&69us?LYtWU!VW>`9FXA?f3uq>wka#-!D&Izd3wDfA!=0KmU61^P8V8uAY4Qt(VsyKK=6){N?ub<>lMvZ?~71uRj0f!|Th7cb{Io*!<<E%d6|3KfO3xzV!Cy`qlfF@7CXY{_*4ge)~-$@!K~q|MdRt`mtw?*uOmaaC!UgAi&SpH}75_UM_F;uljkqy}Y_wkKuefhSTq^ABzXp3}W?ivv7Dgn@1-L9!S27>#%}n-7MUFlsxzC)y2!pY}T=ur?25>chZnC9KYAhIvUrPw|`z~Qa2IDrHwx;t;OZVc04QXx_Ebav(>}RyS@GeTjA+e4R5dCZ`BYf`X4@Ty6(MRYPSAx^17ASOyf%MmlsDpKYj3E1J=`0P=M8hq7j_tsQIL{yl|J}rNnz|yCujIkLv`dbv;{PjnU`KH9js8o8I;bV1KVB8m()n<7c9&g_|rf``os5g6Ru@&7QX0r@?y@?!BiiJ)GvFeM2j%tg|`M%j1?;pN@uG{Hijys}-8?h~vkZvh4IIrYKXzI{n1@srx)ZdG+8A*qnyv&Esr4Zy$WKpRl$4zQuU(F>M_(@&({Q%^uUs>#M8Fm+yZ4!{yDpH&<`|wYN&sr+M&!wyF(2?;h6d<fN>InD5vn3fz1pbY7liu_|_&{|>j9tsdJs_%5Az1)Pu^=Q%za^ofD{y^eIihUlf#gFNV&;XM~gdbeY2-Jw#oQ^4hxW*34su1ilM#o(p#%Ve7HOX-(M_+>cW!yrN?#aK9-&Ac8+sJoJ(Et=ls(dHEBLWL)#-wiMiH(G-s)atj9_pF&31f1nwxi(_|cO`E>#atgST>1L55BIaCR|DP2?>^>k&Ro|g^M}y!(Pw@R*xova^T`U|TnD(FY@t*4K{wo0H)(nP+G<uE0a==Hf&B>%5<xSLFXk`I@T{2UP@gvHzGWykc^-4GuvD(=$ULpwH7a|jY#*%vWC@4QQBFQp8VGHl2pi0Er!(j41HL}s>jNIs13YYVqMLVgwIC;^_roj%@>y?SHJB_i;&>zgXCRTa3Z&^LJ$j&rn@!2zbC<A=auvWyTc(`kG6`xR{!27-uP<)?B^I|Zd0Jqg%VkhV@Jya09Gk#qq9(9`(A=T){X+VgftS(MSp+@|p|U#IwOr<`nMw`rf<RiUyDMEkP1%Y!;H}Q;r}4?yJbNAIn0VWkaK%ny_%P`xhLeaM0hpDK&8_(QfPaJs5Z9~ydf+=gJD8b{lKlP0qYH>ZI>*C2x^B1cZZ1CjczJX4XY9Y#amGl{tu(<{`ad7J<6x9?U`ICMct|RPv4TtzecJ_(EcgMQkG%yY2OWb9Br41xDIu8bYBmm83ptWUU@kZV&t_=W@@jEdwBOaS*ps8NvJ9R2tT@EJ0;wqD&_r#fXH0?OIkEq67&jRM^Oo_;!^nGss?!tDF`W}?#d;R|ckAf#JrIEJ+Y9>ovlR#MdGnBdQzQ=HutNum*i@^oWs3zzDEG~<;aBkw2DEVOt$q~dC{%Npf4IKBI+Qg=9_H}_$JP8~vR`f2*7Sf^fJ`tC&ik@4H=JZbW137t+pb4)fI0C&zk0=8v8<PY+y>l?7b4{k6{POw3Jt6$iSYEqu;YcuXygnwsTCVe;Y%W>fP|pR$${<5L4%G*UuFqnAbvw-s0<nd)N3APSG_fDXSoxDv;-UBje)9fEwUQ;r8#BL;GulQrs9$OaLNpY@m?PbkOxfhA(!*W>E_@;iP#5S$dTH)9JElVxuph)Qb!`3bZ$?7`nFk65!k`KCUDn-Xh_hXAg8elK&jXVpTOvS;Gskx<*-m_qCliXv?J;(K@h$=oG5!EtbjXZgns*t2n-R}bV;3h$S_nHfF`+hG)saNpOqr-bCQolwkGRu;5ASo%@m4?9DQw0%#f7a#0$6R90HLwry&o_$c{$pHrr7}JdTZWMz6FLA&%1`8}x7zzpAhvXg0_b62U9p9?P-hk^?#iY!Xr5E9&#fT){NKn9Wtk0~e=kW$pC{6DDw>>ee65dI~sWtiP~Oq}R>qx7C5wGbN1BWA!x2U$Hq!@qa1JGWL9{O+XstO=B7VaQb5(%lZBATIMqHeWK6WksW#^*-q#&Oz>hS*Ml!7Zj*HgLn-L%=FxOswdM5gV(fY9?ngYuf#Nzh)`DmLq70`9;iorOe>$mc7?#3MOJ(5cDjO+^yC<JH$d8=hX;O{=^Wh2s6}AWq(X7CPup2&jQDtaVw4QZ*D^5wUl2B8vxl4@oV5^f=l+%O`2>(J65k<V}RhM~$*cdN~5}&*@v+)|Pg?v*KFXMKahDJwrd`d(N6$D^~=zxKn7WRWhF8dHU0rC9FaY%Py8r*2L1AayWK3{(``Ex-TNX}*ED|T9t?kPg}nMA|Whnw##w%i4j!5kmiL-3$QG3-v$7px(J&6K6jWAeQ;6+H`KcN@s00Aq|t>pJFGjNpexhYpndxEUYj(13aVeYf$+^~4i1<4So=d&j{b03qTf-z5eu|F9(d`3zBVECqU697@TH3;fK#39Se)0`cCAqIwc^IPp_Z_Zd0j4#Z$rm1jRT1$jYxA&Lf9N3T<ZZxQjtvV)F!`rXG!31QW_jOVe4YzCCH5@D1}*_?)(3DST)hE(We2!t}xNwCojr!)^68NL6Oo9TqKQ~+GSabb)g4g0&7ZZcFSE|zFAdDg%GYu$e5F&Nk*;YCBxcm#h(mLh)wSq&NP&{qH}4~#2_?l|}uq$tJ}XYtEIGLf;@wGzQR1Pe${)qL;rCK)Qy^YXJsUKOn1%*bcbFx8d6-(ij#zK54U^GF}zIKNKkS2OTvhw0)rgZKoBHXbiC1&x+5QzRmY4@h9i%t%2asW@XMS-f(36qHF;E~nr~gH@xUbBzi|0#qz_*l<FG7~NPiH#%j}e-33uec8wy6^wJhbIM|wZv1iGCj2uQqYPM(919a5$0LW<p5hJ719e&gocF?#(}xiA7D*CocW?e+Cg2Abi{LE}NJ#>25}qq;n8VRL%N&8gJDqRLXhnjOb11>tKWXPG+;=(ni#`a!q1BrKttA@#AzRkx&=C6%YzRg%2y7(5kdRbPW-O5D(2FJFzXAd*+C)SR(a_~ZBrvZhE!bBw<0i*Rkvt1Ew!IjBzJ_)W5X44%v8~@HLx)0;>53<A2ceg{U65vjzT){_mR%G+b@=cjjTxxiivEj)Nyz8SSH98u4flhGL(#0k&KllafTbSpE6Ivog9Jo&nLJ)}#2gv9nh1JmG_OSHquVS@QH&$*!o<J>j&x{+=Hzl@jX^{W91wH_rjk<#gX>cyC<WWJDH+MQNp07#vHl%xBi_-<FOIuCraCY{A-BK|0aQuidnT$$X^O}VytIa~5V&l`QmoJ)`QGl&6{NF+T8(`cRFK$I(5UZ1^nUFI-_F)s=Y70|h~T+06Mi9I9P~;oXCVWZ8zvxLM~OwpU8tU-U8exSXnm21PrP0hLcEW1eU`wzCjjvdYLu8d!%sp+kT##Ad@@$^gFN3oG>(#!SpDMPgTj$8f|-g0N{u}WQM+>N2P>BzLYNArd?qh^ljSBfWF&2%{;|jm?qIr!!9KB&BG0HOLgm1Ra3WDFH5Q2#x}P${j;*6m-8Z`rs=N^rl_XM2m9Z6pbg#u6JbrUj$3zMn#V)yS$qG4m_LAJM@*pOGCHH2!$oR*Nn6VbVcx3d1zdk(54WwnRDH;B3fUXSWv2j)rxi$1QwfWNK3HtzS%lpl!zfZrU;ZXT2)5nL5B!_E|WE~1ya244)wShyVHyL9?=M+lb0d4`W6J+5<4Prrj8?r1pA(B^;)-kW)g&R7t7^R7i0`dn4F)uQJZMt;e4hz<ZiB^Vjey2KS64&X5hE~3fmBA7{5vm~x$4LpYr&J?}_qoI>Bi0QLnG|E<$X)}4rJ<!JwTC$XV?h$qmJ<7<)2dq(Qs(jnmsv|wY|t9vvssPh>Rjn7xusdP661vCs1p&$()7xc@PDhSLoOrBNtWGeL?0p7A1=$+3o!*|A}~rVFzY1jjfJ!tAm~6Q(%{9I>XgOMq6EgKAz6|lI-?;{<@GrJ{M<nculCU(V>$sJDQ-Enfjp|ihnBU7$PnVuW&)-v3C;}1T&MO;sVclW-u=*+PciTMZ*4Ml0!Y*R_@Vy?;G{epa`O;uDHJ&cj+I=Ml_5}N00((!1B{<S!=zRqm&=q}?Fcu+eyc%%B7>HdW3fkd@J0xFYs*E198ocf66EVzSdu(p&z{Vu(#T)e6N5spIHXZ>kC_bUET}wb3kQo-1;HriJm$m0s~zSvP-4tb8WE65=*59&JveyPHcAv>Bpd-}DMpGdh*D7&jo(~J8ogNIM@VwC5R^n##LDOh1TjAhX=BtZRs}nVpTN;0#o-(lqC-i&pEP*X5fDZ$<V<1904F?y@5-aE&@NFh=71?hqy!8fhPr5YEV@OnRy3&Occ$tMjlAu4%M-(P)W<k2;~J`8BC~IV@5A+4L}SoMWt5@>NT@53&$YY}Jgu84!K7L^>4Q7y(ili|xW#Nw%1--)J2Yr79uF^+!#>asC{L7cSwn^ycIBcXa_r3mt02oa3V{&ZhQ1sCp=MN*)!`UnfI~or54*4;9BUp!O3BfTiL5J98fML+^<j(L18lH-T_ORJPIWs7tUtZyuLQ8Re*K^yIv30VteVs7mPnDXxp1V_6eo>!OI9Zap_N%pRregN){YD#2S>9zyW^KONlK=m$<6EBX{eFQ9JDXDLN0{}?GLPm;qDE42kF)3IAjhuDhvb443A{~)R<l`9%TLf^mrE_RV+>IHRUs^E_7-rG7e}n@)mr<EIR<Q62OK*9Vy?gfUDkxJZFcCI-n4sw<>}BC?nV`R6~1RDC&}VP!JR)VYE?iHa{@VF234_A#u;OEick9xnVMTbuR=7DM8HScr08A=Deh06{=WNs+%zR5!{ixNJIj)xCN%ThpLQtU(<D{GKUVLDp-F>`duF^4>aMi{w8TeEN0d<&rXFpJH)&2is-z_$;eab*gIqW>ci4LffCVqTV(VkDXMfkLd{xP@W%=R=4>aJ^t6h;6daV+3)InDrbmRUWCWq}eDAygC|QRBfWT%)l0z)FAW@&Z9K48TTGdFdR>pFG@xpJD>XUuc3f1btra*QG%74;XAQa}Q0Tk4ZK&S9(O0^iG9G|~1Cq&ed3`Wr*fqMy_0ZhP(Jj|tLxYuC$$q(Ur9da~05S=7+p5(`T%4VWoz4@ap{n;d?B)OY4li{xW+PXLF^ZxfF&D8{a)~q6UtO%I|0b{;?umlD!KKSeMUbG)3sreQj+K3WW1qH|}ECRyZs+=pf`5|Y~)tWwpChpgFCYUHI&uVpcoO0Lw)7Bb7tgh|%+*;4&o{KMY@K}4@aE{Dic@(ewDsX7%)jCPw(+V<$Im7!);FErgpdwd32~|!q*(0*T)9Et;qGO;xJMw5&6T@QkUGJwu&V4u?<oY++Q+DeDNCH&=Q|!6Q!Bwt^Fw#&vt`u~P;Aylnu1<i-;Y%1t8k3_?mdwRt6R^3p<9R<Qow2k!kxxH1rKJn0?^Sz;6%Gs5zDX|$sd1a2WUQMHu^<${nLud4K)IK9VDt>W?0M3@kpCkaJbrRK*_Mz0<r`B1Hc~|A&}8x)N{Cq+qQGbj+SQo4Map*f7XoexJ>^DJuSU)V2snxJWu%AjX%PNe9WtZ-$P-KZJSDUzY48@}0%=(gGD4^tB{bDghPc)SRS(Ui6txaYHoEB~q}ZF80x-Y|mq$b|g5jIRFY4_S6J$y=UG%0^9l?+SDPoWzhybRMa_ZC-j&G?hccyTV3jPTR^uZy)jAk#I@vG}4ssyN!cO>S%co><WiAczoeJoRtwKeKGb=`4^K_;2NFi{#K!c|#Ng=70{^~*aG#e}#}$irMow8(W@TEQg)r-hpAssleuN%5of1Dcvf_ko*;6IDCbr;)|mj&jDbmb=mf@Kj4+fdJOdt0`RrZ8tWDL0-<M;Q*eHo7MSj$ETz>*V`?W*vUbtVhI=#NiCj`>$N>C`APKRC1((w)r+ZW*o<YJ0HX{B*#;EKYGC1)a>`s;mH_C}2~jdMt#7#1yP8}e8ii$M!3ct5J9bloFOWosB@#XqElLiW0z!8r7+W_Zf)g}haq&#NXy3i_ZB_P)avf#-CdoO10}1e|7!IIJ2Kd>n8<iYR;}{%E2ov{`rU9c(H%)^^gr}usezhoJ$-#*Yey4YZqPbGQMBt30c1U<a0=LZI?jxR9g}E<?8gB`3cn*TPPusHIW;eGwdmQ+|!=3@(CJ%l@&9*g&RG0sFP5_6&FEHhIr>%1gSp4(u%Nn>nqvmuz_~^mNffKHWQPxFkN;#SXeM{3f!b8d#7)TvwP~(sXTkKdx<nxPI&80%&l+|-ZjQ&Bcuh3^jhUT0#l&SDbIB$X#Ffmr<Ah?^VEEKC<B^`=b{BDH$8uy8ms1lWl7r~+^ZqGe3>b!uE+zKZnAMpf~>N&;Rr%A$<R+u{d-!~?(Do9?KN(ai2$*>G3L*}Zo<jRHTU+Zxmnd89m8<Zngt}fjc?PEsE6K*RRtRn*fB4Mf(?j}Tkrp>&ou+t%VIsmolHv~G;5GvCetNXkec97M;fx_m3IuDJk`C+R_Qd(daQC@1vvl_in*1V&&u^U0O1iM$OCAAEd!PCK-#XH;4tLRgEjmsUzn=)1a={^frZLptrg7;=coa-;$VIBy+5<8j`B(6}cTAGV<EY_f6jMS>i6O+rkFIiM6JN@$RFs!y0bhvUF9_6KcoD@n63of@3_7;6FOt3}#hMA&bi7nXygepoO5_!BPS5$^zh&Z_>1;d`i6s_ZeXc8q$jfe(nZ)#qI$^j#mjT4~6I_pvl4-gHOpnzVPu#Xw4YkNF#2kPHoq38#o`f6Ek;H9BBhjP9n$ve)$DUa+jQTf{Gt??-BNk_D|iSa4-8?um<05B1qB*Fq6I~5TFT*{stlp8^P1{Fxc&DT~eT}+c=gt3yAf~rGHfkoOh>lj8e11uptLw|$2xP6AdL70wQFC8)_5@Lo|hc<c(4AC4z#d(oZ-hv9xinhe(LraWxFB)yIw$v;q%uh{79G1$h?E?uInM$F95{Nv@E@+~6XV4*%*5?DnNgvV)VAd-Cw$O5AV>wInkkLG27OdE=k7nvvMK{S<W)8vlY>YI|gwpB=HKV>F)?dhdt;~eLcm=zJl#dg7At@v$1sS#MtsZOSO$rJ^>YZ%ahS?>y!i4S-m^Khtx}tVWIAb>tLc-^*r<hPpPndAxe~r>m?}c!RFxB~;1km9P(60x(`4d_wCi0XvhaNucbUF+Tj>joQ_ec_NfyH+->hA}ClAJen-ZNiX8t8KVB?m3<<&IP6=X5~F_?5EIksz`_R|X}>K({P!3CV0gPzw@1h7>SoV#Qn&g_l-MPUZSU!i0XDIsJvv^Xg>sQZ;-x_|1P2rE`QrN_2xf1(_At{DEPX+AOPTK~Y3OMHs}SPH?5m31hB>TA@;5D<*J#WC=y8%w~o9fhr_MwAr8!>$T$X6cATX(rHq97&WxXcc@1mUI|D9fT0BbQI(q-&n_eWGjLQTC+1G-Xu2sQ9VaF3MPb+iCCGxhEb&2Kw3-lu(06KHZ{@(xq{7FZY|?%u;53mzioLR`n<2-8SV<Tfa8k9zvVJrPup3j6p4Iu+p~_-%=0jYfD*#rbtu6l_fl?ESn~Oxo^ul1gBladTvLQ1}hrmmPx@4`!nq}OjoMoEPWv3jFA`i@WW-KcGKd0ZP8(j)))YQYXw8%k>O+<p!3uzT{rEZFmc`%n3=o+#<3uOKL?yT-?(bhs2W6ruaTKaq#5$(e(39Rl1us>)4W}av+GQ-XyYFNFvIxIs+PAzZ$D*~1lA1vAeX89~X@&#5VyEUk~uq>G>Qo_LDhO8WvUa;Mm{z(uHYpo%1NM^LcT}>ms#&)Ol*RW|E*+rV{GV_Bm|58MOHy*%NfD)%h*4g8N1uH7vGfI*r@$ro!ZL?Qpf%kK?09Dk9^lxOKl*y``!xuDFpH`hC)vg@dlh)nj<TEHMgEplQO8m~_S<ut1$CSj&s@orCMX|$xX}+KA`pvblP&&1dWaoz^&dGa%$?jP{EVGf2*3r(dlQ^3%bk2B<>Uy`jItXl30YWt=`5>7aIl~wjM;qEjR<|TF8H@w6d2=7h=W`^pcAVY)&Pqh`^sd@)4?5vJVbKp;Rv(?g#wE^_8hD?~$4S>c6OcMiJKYZja)7!hSKIUHY31LO^k@M9UPDy^GY}a^SdSS&G1_5S;UF0*AvMBdMo=P=uu0ld0dq5?U8KvL<G|6$M+dN}D2z>#11H6DJ2GOzXLM6)&Xf~eZwBXD55#nsGCE618O!mU05^>iwj&w2M6rlgDS;lz#OHKJ0o2BF@nYDlr7RgUDcvTF8|Y4@h4<l_$!!Sg$t0`?QL-t}6m)QeX_qhfNH55gYo#RyVDwi;TM8}+ORwP_B2<ZYRpjz1Zamga8dT1|d0M323kNybqGCUUL&A2X_%}CE#1Bjv+wtBV7EWD6Jr$!9ei#pX8}<|q($O2Z1Z;<bd_rmO)D?v4Ns8*nni-Hk!(+f=)Hs_HSy+Ah$wH~?e#FhE%D;kZ4aKNJcrD!AT~>$)rR~565v_kLYG{;)VRki#L6}%`XrZh^gF#woOUW%e=Yen%P^frY$~}kz!lf}|b5)yy{>|f;M&X^)7*c3uC0=bn`KTT{N#2#+?-kqG6xy_bK7#}$M2MzWi>;RVb?33w3PdL4mRiQ*SdoLy%#X5==s<Lq;6s*CyfvCt@~WY>fL6A#1#U8`X#(W$ovG?kgg}M<T{NW2Lq-u%Oibdrs}kx~(T{oUM&P`@Rnr2QhOJhYlhh2faS0k5dw1aq-)VA^F|U{c;3VZ}F7fXiu4|+j0~Y~_t4?a&85e``;dFP{<b2Js^?7BE%xJ{|2lX3@M=V>rgtpor8Utp4kusqopNN6Wgr45gv0F(S3hp1;?r<+Kh$JRJC)l-oH&to#>!m4BVq=Zr37}uRht4-i!XF9?9>YW+L^38OHP-DXVA7jdnD6n=Nd}=k28$F@G8I8Bcn&V-ry<uB&pa?X|Il^76im&C6Uuf<&do7v5N!uL5h*o};BHdJ@1ZtVn+o|9#0Wae-J#tN&b%P=pM(sWbQ3ZMQ{eHA=Ze{{$KO9x6pr7x4uqM4nm_2Z@;Y{fJXzQ_VOjj{^eKO0-JJzbR{u*`p24gnHCjvPeu;JS_(l~0ojN!>P&R?z*up;nO$|v?v_hG+f5=GlUjJd8zRva~qgHcIVWA<fvUWL^WW)tJI2udvLD~&L0bg~a1S{xLZ-CWw8?lK-*ke?WSOFr9<;oNEdqV0nUFWfrS}ihHco1U>?+nass}+y|{VC6lV>m#@!DG%LFZtGjIg8mW;Msh(%~2QUmquX%f0>}}_5|~)VQ(s-;mL`bb&Ju>FX45e6_Ti$IS|wa4q^Z+C-oT0%>Z#&E9~F4y@+B6iMEMf#lmoW*18}eNA}W=)4AC3O?lh2m4?&>ZF6>Kk|yHZfd!Q1t+HYrsq0Fbq*^_0-gfUOw{R)?D<xgvOs2%mHV__RXOh++Clrb1)}Vm`E6+HYwK{oP8y+{&Wp+pCi_;4{SGGCWSPMZy>gZ_@8KCzV7^N$<dXxp;7Waa%p3QsH@0(3(-i9*}=Z~^U6>cd1t`HbX{<`e@&Le*ASia8<UYQJPMTQnFl+a8gnI4h=%A5v98emD^r}hN28FBPuqm0mUPeMil^tk3s#h+(u?(;pdFCrj&YyuK8fwbVpmA1e*2OTx(9;cCfw66RTgn7w(pTbGKYUXdkHzD4xEiUBl%CsK2be<G4vVf8YQr=n@Xq#fzL1rF=s|S@O!D>tE3<K(hxh;m$I<1qRTBuH5KwrJ3FEF|QM<?fVs%`7TMQ#aBAsv(@x^432P}k)grVPrKAzW_sgaC+)qz1C2a)Gbc`2$-?bh;TrF<uTdYtd$(bptu?){&<9fa%vPp6s?jgyMvQ$y`Igzarnw(r%KB@>SDDWj?75^Y%0^?vJ>rk||4Qr-dsNtgQe5bceOw<Gzvh7rPy`JAu_OD0Dr7n1i7sBstC;hPE_wf~Fk!<*uxhfn*#LYff37WEe6GV~$<)Xrb$9y9fk#KK#x&Q}dY*t)ovIOiA>9Mq7NA99q*jnjP0zY3PdLR+ix0N_W0F7lMz#Ujgx0HkIeyZb<R|8C^01ZfCIRSt?)#LkZo}MEOe`$QJmXBMnMrJ|}e*a&QR!bw?tn%4zIG<2271i?A_;VvG6${}Z|@+Ld+vn04R<+NwN^5OxY*C6N~qE=HMEPlGHHPVq#O#*gzU^4u;7^R5NU1w%v>o{<p;+7v)lv2O#Qtvx9-QPUx&(ZJI(LQbPxEoPIcNF$l?yZ{Z)p^!-zVq((Jf-Qm9wJv7{8O8V|-Wz4HCEYZJf*Jzm1$zj?7CCZ4nvKtBu`s&c6o#cH#cCXU&mtrLCa;w@%IYJ*hd6$cvb&c@SzXozKAf_}B>@>g*Do>XH=5_)SiLVxybxxqW4ZKl;9Mk@5VV+$Q-CI2GWlQ))QuR_6OMcbMs1LXR0%X$TO74{P_@z<Vxvq+g=&(t(fioS8a8-N4^(^@Jblhr17M=VsN%!jVPqt~o)=`@v7aj8z6PM+i`6%5smtM?Lf~hi2@iig2m~=<31T2|-A0(Ri9L=MD-$OO7fDl9zkBSgPO4IkH6+K-2B>u?7b>FwQdkV%ySv=fV-M*mV!Br8y#^Up)6S*bPuz()DCPn~IeP6lHHn>(cwiy{M81EExaLACK!aCvVlI#hsVHx}WpNgBa9S-QGF6XMazLe9*a$M6sW9$5`GDc4{2V5@B3#aD?UqZ2ba<>`R7OGFNlT;N=tVS&;mY}4ACtC1aJNv*r({qdJ7IWAMIvP;Vv;6#_}r(+76XRhj+84UR52QG|EO_@9t9U9GR|ovGIjIQ#(j%Ea^@Y2LC6uSif3~?#p6S}DT*JS_pv~vUl(CM=JNm#E332k05=!8W?*E5xJc-p>2>b;F_e%wXRa?q&SXNap0SLbm3!ZZ_@KfdDS<F@2?z>mDDdc==Pf$hLWtR&=dIqIsEM#J3hU@W_!7p3R@p@kQ<C2E3B<z<nFvjSNNOR~^A6xfE1`lpH+m!rnSG^LQ+ITOs1<<DDzC0Q>ZIf>`WiEHKnzt!_$ce2NNcoOnaZ3^)?LRT^<aw}s1CaD7|sKy7#SUaB$7)-g~T*4ETVMiHlfvVNxeDL!5|7@lwpOLPkx1oEM!#jJ81-~S>PVR!3E{z0AeSEo-80Km;lNi7Z#9tdoyT{M&)@?70K|Z%TAQ0Gdqea+x%2v_9$hNRQOOlNz9`8cS1*VDgH-E3yQ#_9=uWbgZL=~Cy{{$kxdA>DHpf5{VQdb)AP16Uc^9Yu|Y7><<&ZR#)1TI*N1%kL5!#6!}VX)l^2Z@PS?y=v*vRJ5Ip8_E<gL~=KAfU80OZwi+)6*G(B%4YuK_cDQ%6aD%U+-N+3mGnN_w=KP4{gkR(d(rbwj!>a-nn&akX{=|GcO8ci9E%q*oHOR&?TdQ{ZmV|XTa4JEIgD2UYrG(M5YAV?j?@@rnWV2*<C@8t*i?5hUWEzW?GkqA9$1c7YWH`{3po&z~y5XS?S4Py3DduPva%LbG)NZo|l<19bE><Jd051$3odiVHz4Abm10%VQzqy3>KARhtD5}PxS2h92NC3us}0Ee}~5Ll*M8pIMKsIO3bad<_{RnRuAzYj62A9!?DtpCEt{{yoQMlk')).decode("utf-8"))

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
