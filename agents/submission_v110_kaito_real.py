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
    'c%1EBU2hymlKd+MpZ%~DEq~k_EpgYx(xO07E9@GEVPN-gz+vyfcW;aR??-Al)7{mP84+34!?B<zk2Rd`%Brla%*e>BpZ<0BpTGY0&wu=O_8(vTboTc0-Mh1&zx?9tzkdCnzyI&!KRy1>KY#u0zyI-nkN@}6*$>xuSC4<eK7IfGufJTrx&HC;=Ir4KuWmm){O25e^X`YMtG5pyzB+vO?&|9G<2N6ExVpT5`0#S|&5u_%w{I5TyuG`9{r=Vc@@GH)`^ztu(p|s$^ZU2U@l2BbboSxu-TiL#)2IE6%zr(Nc{w}D3-_aHU-{<t?*50}^JgE?OZQKpFWrybdCm9luWw%e^6>xn?;jVCyrKDPQ=*&8S69<4(ka~k`Qwr`uX_0I&Hbbh@jL&xP$~Ax=C2zaxxBx+OJ4QrQkcNqABFRFkn1pl`5T`8kj>j_C*$YN<f*Cyde!W)a4(rkfZi}YHk~eS?a`aw-M-(i44f@#$<y_i=`WhC`ijrTo6gdJ6`zbJnxp|Mu1;6~ip$ehU;4u%;B4*0>U!=>Yghl+^<cCNBNd5E%?L$0JnZUn3-wXwYAfy8eX^gs{K4LtlMXLQUtitc++4l7|K*QYclXyf*MHj$9GrpVImp2&AG>H!<S~bn+8;U`fi!eFcLhNXCSrr7tXrC18}<2zpMUtt{;;*t@2+k>hS9T)xQ~mYs2s$~UuUs$6uM5XmuCCYunNVw`lCra1s@Vl#yL3hsJUAS*MFGJj`#Y=;aP>nQAeB|f8m(5r+`_Mj-!JYw9zcWMG7XdKHyaZRZyLItXdujT88q7X3GEuWUT^R<!BkC0h4gQY~8^OmY+3EAbNx|f$-_U{B<5|pC8eERxeNO78O5Vee>@A?()O;S9f=RefYnNz7xIuwBgY{`jmh61Ao-nf4~lA3p+?UF%E73hC%LudCH-|BJ&!})}VNH<xPw@(O>|cI~D^)0tk9(^5BYN&|Hh{Ro`%?RUHqWjWo%@)E8OybZ2^{d0WUIYBA&yegm>o2?W_U>=u$8aB_cs*ij!g#P1maNaQAZ%`^Dy*BryIVIIY{fq9=4YnY=iI1T}ij~n6g?l0x@7tVKnsP%zIu3rZq4wJ}rAY+Aw=)>C|L;Bu$_T{qhk;7>9DVhBw!b=drq?*be;UeXD%H(ROYiA)Sh&kY`sGR$)&&H`b5l8Vz4kybuAD`X@(8Od%6T10o3~{kHHeI_nFMJ26A3eg3kQM=J$bsZ6j&iR~$qj;0|B;=dluDX<N7}iPut&F9id316HPH@;n2V#Vh9ej9hh``Lbd>HsjoF&37qG_~`!B@2j+td~u@jQ78i1WR(CUDrolHRQysK!~b3SZDz7a4EkH1(a1Pxt;Hqmt=f}jV#^0a-QMaXwluZM(kQhc9cN+U6{+6nHa$q492z^bv!gRp=NajgM#F`SL-^>M7c=rI>acj;We&GoR*<0AEu9{Bq1_N|~jxqmr}=x=Xt4o3()U3PZ*adjR}%GcmDK_Vi|2oEF&1zsG!8Oi6Eo^6^c(`)CD!1TaLWzCnQ5#j9l048l+9<vrDi4|d~pR4NXS&wp|<)|vE!8E8PJpkKoJD$`1sFoG`INXaqXlwV7i%_TaEMV?xwf0~#Q_voKclcVPa}Ua7Vu{a_zpi^jQYO;*xaA3*xuRd9`RAK($jB{Z5SBJ)uGaScHgt)@nTsSt$5LG}S0@yin#Ru>>akMAY)>_8#e70tSKyY%gYohbRotjr;_z0yh>p^2LV?HlJ9>S*rXzwrv@iIpgPn0@c|MRx2~;1dO&V^vPM%s&0a054ohAWWFQlLI5LA1M=Xo5Z5?STeR}K{l5Nve4mkVEGS3u*N>Oona5<stLmyskz%^d(S<keQhFPK7<*Vlhq{bBj_5_fp{ezYDkJ=o--tO?S~u^6Xaomr9R4f0Qe#*j2K81mNE;J|ovNd=h)h+D*_`)}6a-!_B{9=IY{DfRMszph2(I>`)dJqXs*@Ia0cXO0M*#{LEl@w*qt%(MVr-~?u-))OKg=LqVrSRC9udzwMuLv9;jDw&GR)d`)<E=8j8Bp7zUVLXmTi9scBa7Avb%sWEf^vWYFye(Cf*|8nXkX@OrlIUS15n~jU*V07~9nNNNs61O3MM1xQ_GYj`8Lpuz9?736?)9{4q$Pp-a%?38qc15SjHxrb)9kdgKi>!=nG&oM)M}b4RUJF*B3vR&*&4|WU%44=a8X_pogxHYL4d#hU?R#zt5L+-^GCgLGzQkH`NM`m)N_SSKVIMb`Qs$bgQi71b^eFNcl&AGg<1V+zae4Li^fEx*{(KBBC%FGb2#~5bwPxPqbDyXl5pgBq7Y(iMc~0>MrU<-gdm9LCkaL``SCuCnO5a<#UI_;yE64_rTh7L(+i;2_+ny!L?&%)SjSxJ*|sRES$7%^>XQ(6!8BaGzd~B<68l?r8VPK|gt#Rs{s{4>*FhgP*XVIOk4z5^(6|z>7py)+7(P+Rf-3QvyIEOAm>7fA(gty11n!@Q^9vOp(#slrTD*iro8xO+qg}LN0Z~4fw*4IXH2$S&SGuDN;fQ&!jbGZ@u$G*;4BnP8(ZrMfxHUEi*N!kpBk85>9W>vJj6k6Ub|X;4bbuK^@`po9nZkyc`s)RWvI3flNCbZb0%$QWTxTPU>Z00~u}mZ{ikGvlE6vB@(jmtXUGgxKz>KG-XUHjDV<rmXrCW=#k)Sy6rWJhwNshZ3??b7?qz{r3df;J^BxF|BvlxbhgZ3B{D7dI7za?wq#7J8z-H2A+d^l#nGr*RyogpH0a&1N=C#)R75l03ZwEM7L7PwZ5AjgQL!4nQLATy2I*ZBppWmtlm@_=V~h$nY!=gVS8t^H;}OZxWkbq5n0UiT9c>kK-k#m^^NgR+3|MlFeI9B{l`#3sPH<IMR|Jml2UM7a&6<eLV*SpX;<#2DJ`X=`OLQ7ERei59CneGRtCcSqeSc_O|2YdDX@gE1y@jLr*(0d?vU=F{@)o$7FXsGlEV-XpES;PO(~RE3t<if*UM`az358~7_7A<?r**!^K@ZE?;gi<W~uB}u!r+i--c{EVV-qQ3G4sA{Pyo3g<EDP`6=!PQY!)+G0+pU8UJ#GH}U_0NRmD!MV83xpkuG7`&hF1;@R=nm=vuk<+eQMpJ46H&z@voY1uP>;itSBm~2-a|kfeEfEbnS-fY(UX>HHxx@$>u^OHQ~Ys6F_EGwCR8v}o+aRNTIETsNJwgyPS=Sn4pDxj3$E_t4GcB1tGT>Vq@e1<@*gXO-aR}kw8%6_%9~QvD=~;RXnWJZt2Cp6Mml@Qp{^R$NwNB(^o;GAK?Tipw-@26*%pD!Y=q&&ozOx(9nqB!a|z`AgCL~h)gMt|05~(C`C=IlHw6eoJhS0QIj}A=tgwL~gUsVG66yLBtmP+*;)$BH9W9s?6!&DtS?|Dc+^OrKrR`CiUE$F08nI|)9MH--tX_hd?VwFHM=a1Y7Uug!_T~BPX~+b$sK&SJnFtzh=M_XWghP{*FwKZk`{hv;y1qt=6D{o~RZ}YM{{(;;yzDULta>}KkljTDeib11*09`x%X;{6v&Da&IV5D01RJ@p*+pD79Y1kI@tJg+8g4K~lCp^8s!ecy2~2z^TeNd|ag4@BV#6-BJ(njG{f3n1YAO7jj%>|e#Cu{!#8X>1k?<@LJ9B1bWup`~Vq(G|m4YXm^!m$pS;P-6G-l5ypU8pG0h&9=n_?zwUNX9rQvleNZ1EchD>=thlHtO|1w<#@g)|SiBV|ZELjBC^=$?w{sX2g=4WhUU^US@Pk9QbCsjjHIu)E&5z#TCPF9;K`K3Eeqh&HziFQ98gx<HL|OgTa2sjhApQLp$I1CWsy%SZ3)`1*TPo<NP>sr7S#DI*!z*s2?$^YNK^8AdhNsb!Z_45>c!BV?AHtKRxG)CPD;J|gLuS<egw#e2aKc?=aL&EbjE-3pqgYDZT$xa!FoYXp3NIQ3uBMx(t4&84GgukN^$Fw!O8+XMtSs93~Ewb9>opBgZ2OYz4#@c@ORor;wgJ+VS4Wdz0~rPVQ^fg-^NWeKSMXbc8qG{C`WcJwLDmq0qb+uYf{A32Zf>vg(AyP7^nntIEG@aexk+M}@VC#Vu^L)X4~giYtG74<khM<EO{pyNxLwU?X=`MS#NP0-Eb#olh3M!Y`|O_WR191+iUUNMNoASBKap)A0zP$(<p&1ovciyBP0JCDEdgDIWFm|$<GEqa~sWPG5%j3eXDp}OI4jmSYm)yRV~OovA0V52FKZr%Wim*ML&Kny<4BxR{Dm{_-(+1sHrCi$WRfiSo?3wG#kCq2D3oF_aqm=jkUkBwuJ8I>FgxJlBAWT|_3R=D8Bu?X;w)9omB0n-EYC<GQku*9{2(K_I9A{X87B8;mUK)Ozw!F*8A0;T&3rfB_@?hWU0WrMTRP(GZp<ogDlx98(2{1JT;<jEY-=Akf_^1B9)Br*a|aKP?X`cIUxk1lXLKYSzVf1Td1C9_p}KTOGmWPY^ag~kLrh2L&75P#o~ZLqv|h-7Sz5jgivz|gc*bbyk{9YQ#lQHV)hnzAp3k1G91b{)!<;N8<+*^7ebAQTgD^%<}|k<LUU2*!vHyf!jsXLHiFZZec&C#xJ%GiR(%YY{{j;Gf9=3FBTRE7Jxn5OT7iJJJg_Pj<8RoX7_E>>Sp@!RbVahiPW}(4L|2D%8)YYofiNe1EW6WE_tUqBemk@E{gbGc{hL*LDU+C5-!*$-bv(;E9lm)B2is!>~Y9=T9AI0*{b2fL$QSvymAfh~|K6YT5RIW-rRkjcAyH+27O0NjdZChd2a|l=X=s{Vh_{i&#rVZd^_vM>)C?m<8G|GSglnjvfIxSWpJe8(#ae5dd7vlf)HTVaMM-vkdop@P`6XVKAFMKpk2nWAUYQ(@pT(mlB-u(q!&?fQoN))1%tJ8~UjeE|pXRY{~*{MY6y{DA6p4ggn=>4Iv|tuuREV1Y}~)nYbv`V4OJ0iy{`Dq=EjAwr_(_#H@jID>CGybr1xQYG#@;bo-a(r5(7th0h^@x+cVsWkhI1i4yPU!7kn+CP%9!F6_4eh=YSPyTgixhER#>jo#!+Y`pzh>mj_oEIZq^UIuSo?_Uw`JDum{Ga=H2QmHbP-Z;@5+Lwrs&ZGT|8ohZ6ITotQ2vaK2^uwdoBH%Fo<8aE>JlN081*hm>a8a~^C}NG<GzzuMaQi_eGwN@A))Z7`Tz6B`&>S2fMn-BGmH1Af@i!Sd!g>-p;l@Do(1eJ51qr>YeMi@FQHTq3{6LddRV4Hhu>l9VoF+%A#D*xd`}p{|q3ZyH!W!)L#YCVPsh%SVL5_U=45}p<eVB{y7XRGbwf9k}e=kg{R{jX-JR+W%wM+F2uY?jTqBI+J2+0Rr2Mie)#v%tTaz&@w=G{Wj<f>fYoQoogBhuA5KqW*4VD78c_d{FX;8n0d12=&wt9e>V$cT%1!-r$5I7(Ft%nCBKj*7_HbxE`3G98ycN@zdCoEZeu?g@n>6&fZg(KW+X>r+XBpcL{&p9*~k^>GD^I7a@db{bOSaQJ><S@R<;5L?5t$hHYHD`0k?WlD4R$=fo{L<aN}(1H{>?X;RP$^xO#Y988;15*TceQwKJK&!av$=DoHY3d`AsqF&ghzulP&M%|Udg}H~GAXul?xnHWpJ-?SUL-Q5=#T6XMW$hi3P7sc5=Qu>da^{Hj#8VYVF`I{7KT7G`co3u6Qv4@LHb#uBx1A4Nn=`3mXZ(Kv8#|1lVc_9UOu%Y2|7_UUQs=|gfcp}toV7ZGNG!gGXRItjiURGoOtQtq^MR(g*0&N+X~UM+Zi)2h{B?RA-5-r7l<Q#rgqCxt;z`oDlFv>mS`-wk|1Dkg(<<zDE1k+@9_xTcFctY_iFd`?5Sw`h?omCU75iv9Gr{|1=F=Tb2=egcWm|A%|@Xyv+%b9Bd$*IBTFq_BBRyD%~qHURW8b`T_uD!Fy&wb4RaoU(Fy0$&7hbi#*j+m-BAkyAqm;?;2Mk(LxrykW&~oC$od;I+N~lv&jpsPK?Y#@V^V`>f~};MEgwo3bX1>v75fO5ej??J0!$<TND?Gm)~DNNl2*V?A@G9g@`=Ju&qZrVoALG(?lCKyRl0?Rc#XwT2ogfuAr~~7+X@kHV`+U-{IwPN1_D_%*1jx38D-k)#uT*|CO?y*qnQ7!essv39;+2CUfkE$f6Dx*fVN~YR9yN`(B45S&a-M0^A0c=PB=`M+9jf^KeAlW7sBvjIGA*98L{B~t(GYZiQGs_CI?L=Sy)6+5(4ye8EQ-nY!X=EU%H#^7Q`f6$ZzwhlvPEhT3tRU5VL}U#m$>iQ#|uvUo?ONN`XPUWG)MZv#gvsFCiYbNJ#657ergq(do*xga`!V+v?$-pANY}#EO_U&tszHu%JA-z-9<%UK#A{Te^bESY8_|QRFnlp5^1o{SKxmj4RYhRGk!i6~%-{aAHN~gm4sXRb*>L+yLKjBt&&$LYAV8yhA{B4=9%%8wIht4<e0XP2V@WKdyjqQs^#hNJN*E@m5mAIHI9Bd2i3B9mX21QQMEKzoM^cYPMwQHJ#0d5b~x^Csfimrrp_BUmw0YVtpV&IXA2iq_C*?Te2%l!~l+&>106iwVU)65f|3{*}gEE;lB>N+Dlro0GB*qpYgzRh=ubP=w!I)X=mRvtMpwVU$`I!akbRG<>A3|b#wdX4E7EntR}~$t&tgZhf`yv)Jsay>$UA4^iXD3lvUX}g=LoesX_b%fwH7=jTncA(MpxD3mmk14hfSIN3=tP|2RwbgUN;3l>4rGg+NzkLzsrdtO|bI$b=(M_<e36wbrd7awxeM$-y4b^d&f}T|7J?g*{G0g^H%xH=|b;>vc~HGW!J$v8cRLE0m1sw1`-F#iwYuA`B!q##*Nbg$OvQi?8jpCPl0nloUg#V$wBL_Hu&+4w^L1M;D}A4~#N!<6H;re!%$;SU!J0Xi8t9r3b$uu4gJi<PLW#xmeMQa?ZqO2&!SylpoDf^61~bjtKVqV7u12r-ryTVXTGlT?tpo`*lW3gxIX5ERYXn+a~#-so>;-<YVXq0nwom73eO3<;#%e&=4b@Y+{{>yp-{arba0^U;d5Q^AD$H)>1zHEiz4Dy$v{gicaQpy9C^Y3tE<0l#_(U+bKA`TR-B;_W8Z0_|!knrK77$o0?C=3J1PnG<FKo4krAP(RVPIh2mKH*An5kRr1bjObKI^UR;X#={d)RvR%e(zY(3;nEXMG8>+3JLH|fkt1mdCtD#lm9RjqA3u5I+Sfq7P1G__APp=Z3J}!Xdwt>{0agm5x&MFcah>4-Wu`1^5CkF~AiOdpkNC*Xo+$qB2#Ax!V+u291Ch4ib&nG24Dcv7cLPSakte_PAegFRY=JhWRuHpUrl%i^sAm>6sRUK#JaDnN~<*Tc`1DUFgke1Dp42Lz-tJzmE1qkK#?<eLicO)V@2~RTQODYuNtnNn?;(+tmMluivpQQLBJ%Ib$HKzG3j=$hxNkD1}&P0pUlowW8;RL`vPhUb*@365_4{==!CCIxB^Z%d)1%WbwW#x!VepX4hg4eav;pIeXIjt_NZ5LYlrY;w;m&ql$=Zmjm>%*z$ENn^IXwnv@Dq5p8qM`Wl2YTEg3=j=G7N)L`2<$?=2dolHio#Z8>bk4B*gNxL$=Gdx%TJJ&JA^iy-q+jRf5679$gY;}@@2rFR9BV(i3Rhc7PH%Q4?g5)VyMmy5#V(QbW?&LY{fOjrHW-v8H1rUgePw`!00~;MuXAV?u|*K3$<OP3ZRYIoNz|dq<lnsP%DN9H{Bq>gmtkDtgDE<^SWG4rM_B6O1(P1a4T?z=$H<kQ))oI2(24h8CU({_$cZos8+rDlPG6!xWM6H@St0P;S85FxK>q8G-st_6@{UPHEq#|AeoWK(vzVT`oMabod`~{#J~YLiuhC(VRWR6SMKOAL}kxn<|gR8$d1%J`0myj=je&LNIJK@L#7j-^v-QSx-F`KKl(SxRm^poQm@b_$N+?tx(+S&19~{DGNM(4MY1bJK0#2VKJd}t$;*`vnBYn9+^?JMmxo7EVGz;04R1Cj9&i3{gYg;UTIR5f-qePnUk;k%<uy*{T2+qlu)jrsQT=R`@e~11XLm!wiNk-oCNB(;wu2uOAbORM#t9rq<%fwrC@dYdODp5CC_MN)%T4D=?r2%w>vk=C#6wyuGZ87)Igb}35aIK(4?IpI7Pse+<<5uE1tA+q#DNg^iCT0WLCiRa#hp!{Bo&1z7BfMQMF8R3{X&-1N^k_*F2xJ<T06FTkuLSLo`ma*PujzzGI$*D)mY83#`>%3Fj`(sg`u@BUA|4ae{j}kLK3X3v3JQ1GF)mCLtbr5$Vz2v_W1XGY0lgzvF;C0|1q5m{wg<P0UEkQEi!o>wGb0VYBErFR*4ntvVCB|AqoaD`FWR#f_0Ddn-;mMO_BDz-~A@29`+FRlo0<skBbUo1yf-Hl9;=#6$(!k4gk9)radoFMdkpat}u9Y*NyN#`Sb^;GlXl!(p*h2*a*OH+v&B+6dp+IF(v<25$R<q@gX|fb=CZ&G3l-vUkP=-Xf2If_KUnF2xN^Z?KLWNW6mD?rCWzKrjVBfR=O`8TC|>+xKhunUUE&Tm<je#6{iezMKnZS%POq9QD)-S)e-&S{*2nOGPDcEiUI5`um}|_I;HZ2!?zbiEbl=cer&uHv(`t-aPF`U+NLRtWEIv^{;sG}+z3F|m-L@gK-ZY0SJ>ogzeNF$bgml5@|en|GJ)AVM);9|Gi%<t&j!XH(;cB)L4p5=jozRE>k+<EU%pjs-nwsx77hzg;H*+|?Z-IbKf%e=#UpK~azhF6YnS|)tObPSz7ydVF=-%V)i{qgfbZKVn5+c~5?LD$)c%d-2$&@(3==9Q?Ne8PBwOpOY+tFs4=XM}uBKH*Wz)>z%Pa8rH-9WEV_Ott{#{e-hRbZ-ySI!UacI&YsWV^Jd|IeDDp?YuQL+emp26NVk+jNkUo15Q_q$u%ul?)*Rx9pym%R+S&Sh0Unn79-kMd%5KID*5Om-mp)j_UuD3TQCs*Yb~J{f#SW88@YgN~TZS&o?RCYLF&c3J7_D`#q&6ZS8uhTxY|9GLGaf`^GK>{1#jgU;%bK&WeK>R(&j{%Z0Rx`75marYvr(C@2~7Oz5@#Sx5!NO`B_0@o^u$0A#ou9sz%cbVf%j*e2HD<a}J7;e6_WW>;66}OXsxXIVTsIgYB^$2iwwvh_=OglDrkip2S$((z?37$e&fbi>1TY>bH_EPY2Rd|_*SoQ3cjH~iiP5jD>)QXV7V}z0Hm>di?$fHmJLo*;(6MGCw23K1*esglzAbSuPJI<h2>)1Fv!>;)u#8(|g>ok3Y4=6V)g@%K)8DOXzXhSuI{RbuB&EA-}p@K9oCT1sRij}(MSroXT!#&2QP0_!v7b<xGm6o93lm70ieNU3I)(U&NCDYyg<`{d8k>0zpzABxKKq$1BVrZ&cEq^9Vom>#Wpzf}5-KI^Q>QY9BW>vtG=wSz)QtHZ@dP(p}a^MR4gn8L^`J~Kp5nWAEtESLLP+h|qd%&1de#uzAO|aO5Dt?dBH;<B((g>ndFr{ALViEslIGqtD;@nzpB&|+a_FXlUcZNh(I>#p@8?yJ{h}{zM>HS7;KIig`F-4kiV=#VMdNT`Dv9`J9^oLcoa?V?LHW_fe%(^B!NogRaw&ErX^b8#gEh61&h_F{rMfjDzQdJ<yjgcgPkysL{V?kg4uD%G|7fkbugwm5%L_nn{%TAbkIo8i|`GGYQiHM^{E_fdxvO<O)!A1bFDh!-KWO|{c$a$Nw0+&R=s<q2`iCSmD_#><H45h9fUSyF9eIV6OtGC$d6v><wlEO=XK})_>;puJ@e0tE`kZRNRHrPsO>57NPV6ri_rD9H>a?%V?Ps2O%Ix;6fi~RONKf!SLV-Yxbs2NqW-lY*EWrOY|(~Y!ZmgyMjsZ<xGxAfA55d}0Zhwir6P%&FJ-XH>}EHzyY*jwC7*ddL!jZmXPxD#5J9!=YXNmrQ_7__A2^JADG>8__nD~tL!K3SyL*KH~%pz;!0P4@#{bBQ3|{6;WL%8-2yl$xK2&$$lmsRG6l)yJfCtyZ8icK%Mv<tNFf{IDitMxg>~BLL~mNr`r(;B7D)8S(~e(#Gwzn-H!O4y+0F(R0~&lqezt5yb{@fA9^yPPHx(&m1s@EWy{X7FlUD70v!$esGa<j=sbuX5I!(!XlBNV<51eUR|VaQ{B1?fCSu7JZ9K(xoJM^Q9uwTYJIhYd-z?XzpDz)1mNl%EBCXa>(X(CJ1~C2o$IWszMK@2dhQUEfiY0DH1LSK7`T^1;UI~VT))7Np(I9{)G0TilzCH($~CN3br;i1qD*MaUWa6>3knIWv<-m94E>_`4XxFnL3N$VkfkZJwS<4X!D_2)PB*lt@ueC0R1?oc<&qQv`osnaqIbOnU#-0Dh}Y2op;L~73dJ;#i~^x;DL$8mxWR$Yj}kD!3ib+THp7(k4g&c1tCO3I7^Z^JJ7yFKhgQtHvDN_*GEPb-(rT6}14BF|1i;L;WPXUPGU#MqB{U$guT)H6&ZwKJ!BBEPI^x<uF%n}j;$;)1gXJ*Aphho%ZB_uw@{{Jv_)*>f>c!_V4H?t=ERD2wA2htAP{NolOF@{PdnZz*Q)EB!uB9V#AozebCkzYy9a~%EZK8Ma+=V%>WMEOXGI4k*3PF5yZPLKNB!9}iD`fQS8D2KUfU;y8869hk;=G&sT!rKlqqBs2fi7e8%R+?`+__Ze1OJb9m?3oo1qC#lAPC~PV?-!{7Q#1g^Hc+c4~3CxsbYG>s209&OINAe4#&JOuW%2M^2#WJ$^m&F!wPng5UTS?mHjS%LP1%vsneS2M1N^!J0Nz#TI`^=&8tukL7<-J&@ycMd=SV68-h^&t^j%A67`RQcL)aZuS_mD*)Sr{KdpWeiE&7QER(1SZ+_pg1rS4^bml;ppHMs}b3G2Sz3^p&in^9~KT;OTs<I7{_aa$Ku~1}8AqbLR6XBbOVgCI8#fqP_')).decode("utf-8"))

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
