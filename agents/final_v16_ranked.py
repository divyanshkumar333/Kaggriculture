"""V16-RC5-PremiumMarketLead for Kaggriculture."""
import base64
import copy
import json
import zlib


_ACTIONS = json.loads(zlib.decompress(base64.b85decode('c-qxnO>Z075&SPY&%ylAhjY`~Ojd~2GGsYKVi1c3k|02k95%TH`R~zM<d8F6U0vPp(b}ArE0Z(t`*l}WSAY4>#b1B=`5%Az`QkTUE<WCV`gE}yF8=n@KmYu%=RZ7u{Kro}|NSrje*XOB;=9j({PE-C!~4(go-T%q?f0A8=l?F&yWz{l_jiw*i{QgAKfnEO_rvY|^RM4MY@dH?{`~3t&F169us;05r_JX5^Phj%+&_G{7%pdj-Z$a$_?q2+he?0#-u?db$CKBMJ^OO8-F$lb+OF}#yW4$B$Df@x=VffBBl2l;e}8PpTioguZuQb_>|tal&HeE3`1JkP)*V0Xr_27-Y4GfY`;MzG`R?=G{rexE|M%(hVVt5j%zq;H=l=HH<~aTf>1Br>fw_MErw>o#j7(oT&iZeEnI7p)`){5urrW2@qxazBx{4mW|0W!!LmytIc=Fu&2(m$%?QrzmV`p0C-uC7AT(IRzGj2LFKA4P_KF_ubpB_H%M;Z)L%RJi^dhE*K`AyS&(q1z(ou_#`SjSiPo@QmVTBcbVEPc9d2gcumF`9KHw~P*rJ1$iBPq`64Ihtof-?DmgBhzd392&g2tuGqVayvv_t^zhP_2*6v8fZm%%d9Zy=l;n{Q(wJd-l52T@^F8@dH3|=Z#R!mclURH`Z~kb5J;JG;b?$G2AV-0aJZ6E4fU3G!{{WNeK-nxPSF0Dsf85(rZQIf?b_un-=<;b_z8D=_fFo)yq|iUa}U=z$k#jlWN*5dyZ+Ym_T6qSa_;PC<iy8?^|qk93m)V&^=g-JyM*H`I2cBoqJD%QFa6wE44bAj#6Q=oO&LcaJZKN*O>Gpw5aL0ov}5ktNINEM;E7XNXwz|ED`PWtI!gTk)8&kK*g)oR7tXg97qH2@!~JhLq0@$K%N;faDi^aqe|mbn-F~-ueEj1t*yih9P$^$!pkpcDX;BNMZfY0f>_fK;a;TZ;2(RsbH@4oA2iN;#jpl5F#jfNc4FCeJyp7+x<n{?$eLM^C5H<Th0G<e+3H&g6TQ^-)Q3nimoE;%Bc?d5CPG7_F06Qr5DrrmIkVDnrJFbV=Lb1lgc(Bfb2B`z$_>dWPR<uKB$YBj9>;>BCmpc!VN{$-Yf@)N@dSA6h&}t7X-(bYAo*P(cH&A*@#TSW=-^9qV@Ul4*Y7d+_mA@>w+s8l1@e|}R+ky5%KwVsM5G<=a9Xv)4BY}f%?vmyjxIZ2FF8OuLl<vKrwl^^r$Dd)Z)<)kq^{d6da~qxD@xDvVnru6RiOWwVan3pohv!PR#tVg~HMlF8*PO}jaL|J_p@ntebJbmixjnMXSStm89oY`CL+1N<v8~qbF8L-&KXle{#(EhYHRhT%I>M<U)U?tt+7+Y@W9-UFgr0Z+tqpLz^v2ud<wI?a&mY$Vx^O)IPI2_y_2Wj1PY1BjvIqz&M}7nEx_*Nd5CGOj`60xhI8KG!(PieUR;Q+eS&%?Pz9|f`%EJ(f=?z}<O)l^HOr4tCSr8@>ua|)ihVM2250=afar7zWesR4kUyX_TmZ3@sCPOsD*u|{Gb*+t3GAaP1UkE*jn3B7eX~0oN^?MmF3A@8S2G4N#p!bgtADsy%w$yR6JUra*(^J49J?5u8Upnv2v26QbK>_q?>((trw{Dr+y}B{Uy}I!^<BHLrOuU8TV+~9-yWM9Gsksv%{Uou@*yW~7d*awEglsF;$jj1yz9z&ZwN(Dv(!E`mMMUB2V^_er91=kiZ#$Y+t_e2t7L!3%dY4<mJT@d%W*{giN%GTK;S}`V$Y*P0PlyK6z$}8)=&W?JlpRUHDRBB?5BDUlWS5c6b|GUjU@8El5yC4vxtiuT1UgSNMu>9GGy4;a30*|Vd0~Me5X6#~M+?EzhLm{VGbEnq7r31XuuP481D9rTqX0?|Sd7+svj%M=Z^Q)(1>=L+`06qshBJ#;hKF%^tJouKX363ChoN=B4b;+QfZ;MoWTfKdPhX4TC;dj-ZUfMSagDsc`yFmdtF1#aqun7MT2hrNw?Na|ln*AKwLGn<*CrAf(qQX#z~f%k{F@wVn~IbkS#(gpVvY*r>~G(-5j+*@Be)*fvU(~}<Nx&B9Y;*SMwhz|NtBU8lJPv0q$2EXSR+PX373i4)*TAhrb(0ilE)^PgK>d$PN0Rh;`mnY)@TmS+q-aXo-{(?C&4@1>r6tHLe&HosOvp;B~LhZ)NJJ{>jxOvz-T<aZya^wWyZ^dq3_m?ficqDRm)xoO_%7PtRz0z?M!hCBiB>RZgZJ;9vW~Q2Dol86};1F<XegpYodYcV$U3e;7F4&zmKnW74Z}MDuAuD@F7@8%I>FLtIW%!sPQtGG|E19MtdTHZdr?b@uoHG&_YRNPER&Rk(>2PY$|Z8zM7gyZurQ0u0;??T%4N5B^z0eo}*XW8Sj~^3GVyQOjZwac5Ytp3N{{UV~MjNu_7QnUQ2-MpNDFPz}oCOw%@iY#swLzgHq0-pBkHi`r}uNh(0wL+W0)+CBP0F&`zi$*v#e!W*1mxErAPU;vwa;$c2lyI55W1^oDMuJ2**^5rDzlKgpTJ`@{5yyZhe@HVwK&5cdgsD@~q=wNg$W%^a3;vP>!`=eWG1v#f<!teA1SNv<RxM?0ynb|IPW4*g>kpqnYp?c9dB(owJLNaqA|_ZC+r8q-vu`nnUkzjT7`x*uSJjv!dTzSKnIp2-DiZwMMo$tq3BUI6GaMgWL`Zv|&a{91pw*-O$GIIDx><c(dimWjnis(z5|FAMgFU9S1g)Tad&y#>Qg#F(}DV8JZi3j^}lcKxH(!@W0Z;Ol<ey6nfH#U<DTP@$a2->bN8Sxg5guhjMkNWMayr4u(BiHbz*;9;j`S!<I+xi<-?aX!f~nn5(G(Wu%UjA$xwM4a@MO`M>xH$-0WQYUJELpY;OwGcsE$f}t~96Ud=HT#M4XBsvm!uByIO`$q4KRZVMhv4hfJ4O8!M3enx?G8;Ik7NPU@gK*v4;+2krTIF)@|W@@*#TEQ7c@h1atoT8kJ+IrEmwR5@ij<|8?Z-bCm=n>EYP5w&0rDQv&K?3VMhXhO7r=XI&JF8W7ms43Egv;+N6b$7rOAlx)~1v;Lb-)CYS)I*P+BK#{)%QaBQ?}yCD4O;}`6iO@e#gk>rC%;Zh<-G@E3<4A}g14~SnHLEP^kE8L`jPRc?n6b~6XeK-^GR#}(lK*RjxHUSQ^23A%GV4Yw=qDEISqDE{BHHD#Dtu3j+R-s|!Z(it<yE#HNnCcAi`fe}|LMXM+y`Lx4UGO=$gkb#Dc!v~xNsM7LcaD&;sLUu_1cg|(n{1a}mOM&pVZAE5AoS!3VoNnWa_s3O3xUIAM0k?JoG1#ljBOi+5!g*baqbM_Z5wi8%I{OGn9)kdH78ZGNDNZ!I;A!WI4etOmTWY&I|5?u72*WtY)j|^W2b7=s-#9Q!*@x@f|ZD@@Jlq6vFrzP#?+KmnX^pGs_@noq)Pg_7v0z~I=%NB3`Bvg(joWp|H!?h4NnQ+Va_#(a3Os=(YqYKc6zxl-G5o=?&pmz_yJY>0GFBqpp=x^QdvjN)bxm$#g;Vj!r7g2W{(+lS|)L-1do=iKs<X1hr=4S<B!B32VC(|DiD}r>K12gJy}Q*dpMB1NjO{yIyO-#wnGHy$y(AUjmY<4Mo>`%Ns)s~e&K|qIKW1QKf=MI8$PpV?fOHdD10v#q+d|hOVhf;djR+vFu)8q4RgL<$lO=W6|TTG5hfcAsF!@{SO|eqfpzXU3<XX<HXE5^kcS1~7GZ3k6FT|nC80ZXsAO7$u8=iT1g1w){t5B<8P|jzhq-hEyN-<R3qV2jM33=l)7h--0gIt&HE%3C#T6;nwRTM7GHp{xyi%kxo?okrn`%Xu91Bf`bbrvTf7Nd5d19a~iNT3@ClDmn;_x{=81>Wnqn@%rDb5?|9ac)EA*VRh0*R3Y$a7FRBeB*Zn=1Qk>r&4<SC=57J}j*-Rl0Q9ukb+ZuMx~x3~Fg(N&+@$%QkaRD>5=c?lFm;XApcbWtPTY+@Ms|8V3(d5GZqRwT~g3>B>8KVz4es6q&F9|EkVA(v$TWOtZiA910lu-grw<(yMMtn})b>Ru8%%f&0Ww@$;c<QcGVU?_4f&L{N@$g&HKF!sr?QOXo13^2&lV6XAtgN7DX<v0%Th)AjD$A-$F^D)jJj;i_dOZr3GA+K<~cRs8TD3ry7@`KwT!LOANYQjDBa^jei2Y$G+|UEmJ@_wH?bq3=jCUoRBS%)5HMFfq=M{MXb@IVG@xh~J=wtrPYy+X5_{M8kvqVq12p$BZ?S*IzN!B&gEE!Y7ct9iR+5IuT;f>bbLoJ(_@7Ft7RkQB2tOAwX>a)+&>@(CHQFnjN8_19eLZY<?z$5^gfcxjkL%4cA}VJHz_6jXYmc+=5A!p%O9X3~PEj3v{_kt_}0Eiv2EHgCSbjpoYqfyIC72g4l%sU>9X9Fe=A4SP@xDR3!<UU%jJ6#*GKu*n(VG53Q0{rD3v6$jH-E3r0*7!)_+c<tR*ryJ;=u0(X;DrI>OxDUoE5at1jyvxl-&!C$3OGsiz|6t~J(dsjK4RJT|vc7b)`*1NK-t0E`M<<TnEpLBng(!v@{9dZ3<3I#x`D46@omay}Q#jYr!ZnQ{xYz`t|Is|TQD%V8i#IeLdPxFanGv!207$-C$t`ag|2H#+US0u<q1Btod62l^qB8ytGMyMuNt^LlZrI9L4s<K<Kis?X!!PoQPbo?+r9huR_<^@pV7}-J~Lr`4hn7d64H|pHxvM4v<Y^VrOOPQUNT4PM;q}u*_6T6~`0>pSE8f)kj61u1Y;x{>@lEAABNy3{e?-4GF9wD$mm#?6&oJq!OkWntg!dpUyeUxONm$-8OC6s4|zq-Vmf2vS8NF}4BI^ceqqJC&8nmc{shC(=#F!TgJ`WxstGY>Eu-J~i<T-t@BGjjAZp{19pzT$+H*lnvhTg==#r49oqIW8q4N?#=We5uYVaD1Ra$g&|-dRR*~JS*O;Wn-ea7Iqax*SnR%9jd1?4R*F?nN(e=91a38P%KBs<-GmM0_L)xv{Zs-VTH#bC|@qh#PcJn6}N!+CO%fUA5H1Y!lIE1>yRuk5F>;bvUj}Wr5R_LGU=qIKs1lFZiHi1TP6U_#X|_L6+M1Uc{Cyk0UD$?yG(!BW(@+}xU3R9dlVfPDc6a~0R?+F5Gux-z^m@r04LkxEON4Il%-9T>6CEyISPK;{vxLU^UoO3upvK<qYH?ZV!q_H*i}Xj_w8bR8o~7n50`4xS|W5C5l9PDPkfq}%u!)=k=kN0Wg#mx)jeJI8}q=E1-K^Q4`vYbXNb3C&B|2qVrFA9;_o^OA))!YbcllN*}!4QaK4J(7D!Mfe6VdTCM>A|3sN5h_GY<k^K&=>jVjAcPx7TwB~6(+V2Ti!K}y5by~oz2#|s%zA2U<ISe|n!ASSF<QB1m&WvUz+A{8l)i`fV!XcFoqp2q}ly=|13DNQnPRdpA2e`qZWG<z5WiP@x+(8F4Az`!fRsRK6!?3ZdhD?=FU$?Zm<hOiM#KxD3J+>k*zgMmu$Kq5jH(>OZu=4uYHtV9XCEPdxq&nJPu9Nx_e_QuAm0Nw+ei}4GsdoUeWWxlLGb`mqSN=-5Z58@DAvd2Tto0kkcP=J6m>UvkH>O48UZeEjp-ic-K%4)!@ZnGf*R1|C>dA5aTwCzOamZW>+qqW?s4#GZQ=-5fhwJ7^Ew&tmTj>uZUA(-B!N{p7E7omhXvEEz&Ox4lGJaFdA@+zNa)YPV+YM8y-S4>N1_DB3}VAaOOfzPoS8Cc<)8(~bVB4@VVm6$H!hQo_Jj$;+%2NxLz8>c+eWQfL+E{qzzl_ZU~Ay=ELJ@wMr*fNGeO4c~T1*x!CB*ikuNMw`WAeA7cfKX9umFC2Qs8jHGUBf0qL;z!Df%!@5fK~<*!T^$Pq!-#Hj@HetR`S*X6@5|v^w1R`WGx!X)UxdXW{cY+f{cmBD>LBXx{Qz^Re++|2U5YLTKog5dfNiJ%__u`75w(~RmD=(mU`zMw8xcwO|Mc~0Xvv{GQN{5pht*%)wfj;j#TD)I@(<kh2Ez5l~Oai<^@DKzf8#|xJQ`GXfEMYijwOJR%ql8H72Pu&$EZ?{sl~J#JK=^Is-{JMn2zR0F?Pis+-Z|fvE1PHxOR;&ZUaRBk&|0Uo4SYOGph}r0MYKQA%G8D^N8FXMswHF@uiCGz)}pd`3AMy0fYpZ+EGxp|<IIr4lW-%B_vtNq8@+m8Rv*&@3d9AH*lc<UztD*2Xfg>^2V+K%`7EQfJ1?jk69&<q`yEF*&=mI(iu)YN191<^{qkOcd>OV!&F4MNDH>T*P=u=vE6&qzGs;H6tqs=M_0jz{d3kr*Oy9Ng#+Vyg~5p7K?Ou+z~1nR@&Sy!%@Y7>&u>@Vv!x_WF&xtx<V0(9J9hUWx9ZF5rTfg6OB0p7BzW+isEzeYF8<|HKB>TF+zS<X&?p=n*)%hRQI5onb4?VvA+8CsoQfv>9QzHQ43YedV+b%N?hKxxSfw`MnbVvesSe>)g>_?hX<zn)x@bI`CW3rkaxCb1Uct@BEu|<Vg{ZoyTT=LKs=Y5`-cypHtkm7eg%e6nl7W+D^0=`Bn#DUDkyPA_1wjnbZROjQ46W48q0omTqDQk?7_(@g3^fX(yI9a{&eKcnn43AfLKNQX<aN6wY)`<9j!VXi?z>=n1m=)0!9*UNbd%N6iHHv86U|kt-{-NT9pT@Xa~YpqRY+>7NG~WSUl@OKoVeldr`d7aqHVMNeD{VR62B=$8eo-7Os<I5U#d}ZLKXA$!4O$jM@A*uRrsaa5|L-rSiPMAjlX?Yn7IwNd1FfWA@FoY1pz#tvG>h0|Ye5We1rfHUtm|yl~$uBNfdAQDNj-6(DA}uVZQ3%%E*PiWgjpL|H_{f`LlOJfNfGNU{2=mXl>kMtc00Cx2!NalSpplJ*zo<u1`NuBKx9A0}o^rq<7`BMLC~6b6ba5I0&jgL8`;Fre#BJgHjgQN~xS18y-;FQ$IId)OYzmLP%i^VJersztV(*s5Zxz~*zPsTWbJ5BCO`?NNFQ|7OhGY8A4Gij+{{KGHlA$DJ!EcNV&U{eXujmte(T_{x#^c4bWj5zUx)FRR1DUCGUtL{1ccP_5F3l*bvocq7TRGH}0B?e4&@W<5KpTDB+gFeBV0_?&5L21Ou(xGlGFs{A)8nKQ`yCA3J(0mVxxI!~;D|J~=i`}aRS+b2(-A7kx5o~A=OfD+5)g9O;X&p&>*nOHC>nIG#CfR-Kxy_B=He*-#7$UO&xp#dIAMqObAg9-$>LUoJCDBu~L=wCU=(xs*^LAnE<H`3e|OZ7-#56N_fP+=5)0HDWVl}~LI!@17LXuh#dpP;@6r(Y-^r5@;Uk*j2l$9<`wbvfvaSJgO~Vwz+`PwFaB5XAJinyE}wiHSUMoOa9+v8}392udOyuqm&4S*o2@|3=TE;P4aSdXaG8OmA#}yL#P>&#c~jyHc;`<VBsMK+mdwW?c#kC{ma>oD$Q~edwi_<3nUfL^!3QHL>WxJ7Ps|A|_EnJ4L1u>9t68nOdK{AD&A$J3aG`hPgu@yiKuV2-ygBKXJpC>F7uxNNp=2K{*p)3+fY)6rk#cK_jFq4=cqg8bp5NEI2ReBT<ttS$?wwEM_Ylc;<SpAxaIipd3g=>yZ|=AbD6p14ucV+^|SXNzbxk^T^6une$D_Xj3JhSaKTy3K$Oa^$3bYpAuL!Ey|N@oJ2{%*A&r07M;Z0R$$iwzZZyGRVihZDpx8OAp@B(xgj&_jH#-S8ra0s3~f8IoJ6e^<d8B6naWC1bWmA43Z+l1*l=DTcKw>pYje4gN`jIj`P9p?y{tO6@M%|S3D%gseAY@P%#b2~(H!Nh))BIBf{G_zNSpGg`H=it3Z<xJ;3BSAQ*9MAX!<oqU2XI=6Ff{*)VbVM!sih2P)u9ZhGdM^gts^6sSXXHc<ilE@fqgqI{`s8bbaPzm?%XI$LEt$G<La)p=F7B*r$M|Q(G@`Ad*#FV;c;F&xwn@C7f1~KO`zMY&YEtP<qa=&bX$@B_iBaQFILhw(#U|5?Uw>!KH~r&6|wUf@Kqld=kcfXR2t)?JtBqodqVB4GnNBYDSR^nnWEkv}<$`<1I+Cs3Zc@V>CJ&COW7$6+#Eo{o@u2;zQWSk^`W8w50%KhTcmlKh#kvo(=wPq7dLo9-~v5HdsT!!c$VwjqYe|5<xDGfHVg67OkAHU9N7`sGPar?D~-$YA`E>Knj}8?2CDVc@@bg#tg_|m&rx8GvFWR-^u}>im0>2hd?uk#<FdyTJ$_F=yf&`V+BehC4Aembef7T`RLfHScHkDH7fZk#hObQ{)Z?A(}KoDScjr$6LqP3&Wu)RDWy%)A5_D3YZP)pu9&EgQ)JyU+a|hjWhGsAvt=w-US^5grJP62eR7d`v)bvTWUhbfo(HU%S+PjD&=Qn|m~+L5mKbrFTk)r8YXUoq31+~vS8;(@NbODRfO(oOv1FkP(lE_QF`M)<L(rmchKpW}Ds&=ip-*--hnk}4U8nN5d@MA~;ew{MPwG!@!j)3^B|=P&$rQX`8^_>$_12;S!d6J?Piq6wdR&vUV(n;QuQN*0o)T}3Du;ITT%}1-15MNmb~$Mo`A4Ei)mot~kn&|>dLcx~2xN8?t=NJcsKZVhC(V8kw6vuLzRd`OixL_n)DJj8Uh-{>S-t61ElO!HO~7Wh#4<<EsgPNwNM6UP&1aU=ZOkiKdr+>zwpm4ll_q2%Su|NB(@=V+-Z&|kA5dk)*10C^83-{f+XVJOwqBFPwibzW4n*To8UGZiV#Zf<LR5n1B9b5MHPEXvlFzdbIMQ1^zEX&|Tsms$9Xx1FmtKsJixQ_Yl70>PEk~cy`CS4Hi|~|aCGUjvTs9$v7FyYeQRWPb1{h9c1BDQW64j3lz>GA~Lc$$`0_lEnr2xx615Ja_-Q`+Vn)}OqpEeE#M{Psok`Fo)1DC}dR`Cf#VW=o6pQ#T~qGK_H&B>$Stjp%b={3Tx>imx_Meo3wSQ55P@6a%L0G>I4f)}IMlOvMrGUpal!%@SSE$m#UggBDb=v18>+zAs)KM~vj>=3=sDXSvJ6j&+V7>f#{d?-bhByTv1QzR%M*XkvuG%?apA_LCKf*&CsNb;f1mLb)S!*tX4ScOav%5>Cjr?+ujOeS?CYZS5PhV5SOI_rgK13hv-Hw96t^U8;aY*%(0>77~aUQcmEnkbSpRHT|{jCGoy9f?{tqEf`D;-TX(P)s4Hf(jgMm&Ga_S$f~OCVbQ^X+tdVdtPZ1FZo18tQaWu!dFtt(C8GKNaAEG%%Orq6`>}MVriNg0cKiiU|0i&m*1m@AKK0(FoVvEy_RO`K+y@~Er>>v5<R?g_Ye0tw+i<(K?maEjG!}IjMUgKtlm-u&W-BJI0C+@igAf^D3SMDOZuP=d_)kUg(WFcRtRkpP%}u0U>wS-l8Vy4aK?G&7L(4OCbiVssX?%QJP(XIDME_U7E0xhVX_F|M@fAVbYr-5OVX!fZcnByS+$jlu*{)a?cj$!UrQY|iJE}sUw6xvkpvF|#*6#Cl@F}w2_9;845`YNR7nYdkjaJ@q$fo#O(_sXGn^a9EvhC<K*tWGIO28!8%LGL=0+LI11hdbvF<Uh-CcxZTJZ~}E4kGx#whdAgW?`(u~0`t#D63mOOl7d`DZHYhq#!zpsZSin--S_yQO8-Ve=M;iDVeEievUzmsDCRlSva~$PoxB=ZEuDN17N%2?%P!n*w;ntE5rVpNe?qE~Txi!A_$CaMPy_02{{JD#E=00kBE#iXuwLI%hRW0%IcF$x(tVs6@&kbz4J}qR@8m1CXCZ=s}8tEeezpR<zAy-lkITf_dKCFjBF|B&CE|Yy?-a)!IcF93vJmJ#mFli){=^cCb<rWD*4BV}CT2)(})#YK_T3+BMJ|)>nNT`7Q#nZDfb4X+a~eK~Xc;LtnT*ZekM$J{q>V6(6pLjmEr{gcDA=mc{zzTS2QKtM55K@&qDV*y5=E8m>&s>>_Hw)yk=JN_!%EM`IthPB}|WMwY7okGY6qpb`-o%u>!zZfsJ;&(N+Yxq?(qL`-r-Au8#hD?luIppeM+De6E$JLb+}Gr<SBn)AGIoE5`Q?;LI-SI^wYr0>i|jczki@?_x03&5fZRNBi-T0UiW@C1A@c3Vu$_k-5n%o1IJILlqovmT91%Qd2>FA&O9q!tb-1cO!(%(@heT23RKu(m3x!_geGq@ZUYhT>PxN%>!m402b0C{KJ>=-%XmQayu&%=g>jDzUr@uNGSs+)=Cpm#fa<<<MKql~fLm24|=7HmL9?yM$~zT&<^^HOmoS(h#9EayB4HEk4x*Q`A&athGRcCZqVPTzwNUpQXEBia~!mP<-Zt>djLe`(~HPrEU`AQ_D<Nniw(65~Oq*O|5cT`3|6bOSY`*>=H#<Q4BRF8kNHf&@1!`tjNGlH7#a-#M>ag4vIh|%MocU0Gb>*CcGA>pT<Z_3Uz_YK0@`Pk)yw%KTa(;wBDHlKl_#rq5z11nhcamYy)qZNQz~dij7k>Z9_C_=49seZE1r+oR&z?fp5=$$FEHz1hZ7emo(()!<&BsESow1n8whSLh<YU%cyThLXAYi{v_TMI(Ms#cUP#!NNQ_VM31gB@_4)d?*0c(Djk>')).decode("utf-8"))
_FR_ITEMS = ('MELON', 'MILK', 'STRAWBERRY', 'WOOL')
_FR_STATE = {
    0: {"last_step": -1, "due_step": -1, "due": {}},
    1: {"last_step": -1, "due_step": -1, "due": {}},
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
        state = {"last_step": step, "due_step": -1, "due": {}}
        _FR_STATE[seat] = state
    state["last_step"] = step
    if 0 <= int(state.get("due_step", -1)) < step:
        state["due_step"], state["due"] = -1, {}
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


def _future_quantity(step, item):
    future = step + 1
    if not 0 <= future < len(_ACTIONS):
        return 0
    return sum(
        max(0, int(order[2]))
        for order in (_ACTIONS[future].get("market") or [])
        if len(order) >= 3 and order[0] == "SELL" and order[1] == item
    )


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
    if int(state.get("due_step", -1)) != step:
        return action
    due = {str(item): max(0, int(quantity)) for item, quantity in dict(state.get("due", {})).items()}
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
    state["due_step"], state["due"] = -1, {}
    return action


def _front_run(action, obs, state, step):
    if not _FR_ITEMS:
        return action
    private = _get(obs, "private", {}) or {}
    shed = _get(private, "shed", {}) or {}
    moved = {}
    action = _copy_action(action)
    for item in _FR_ITEMS:
        target = _future_quantity(step, item)
        if target <= 0 or _town_demand_now(obs, item, step) > 0:
            continue
        stock = max(0, int(_get(shed, item, 0) or 0))
        reserve = _pickup_reserve(action, item) + _existing_sell(action, item)
        quantity = min(target, max(0, stock - reserve))
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
        moved[item] = moved.get(item, 0) + quantity
    if moved:
        state["due_step"] = step + 1
        state["due"] = moved
    return action


def agent(obs):
    try:
        step = min(max(0, int(_get(obs, "step", 0) or 0)), len(_ACTIONS) - 1)
        action = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), step)
        state = _fr_state(obs, step)
        action = _repay(action, state, step)
        action = _front_run(action, obs, state, step)
        action = _align_hands(action, obs)
        
        # --- NEW MARKET OPTIMIZATION WRAPPER ---
        market = action.get("market", [])
        private = _get(obs, "private", {}) or {}
        shed = _get(private, "shed", {}) or {}
        
        new_market = []
        for order in market:
            if isinstance(order, (list, tuple)) and len(order) >= 3 and order[0] == "SELL":
                item = order[1]
                if item in _FR_ITEMS:
                    demand_now = _town_demand_now(obs, item, step)
                    if demand_now == 0:
                        total_stock = max(0, int(_get(shed, item, 0) or 0))
                        if total_stock > int(order[2]):
                            order[2] = total_stock
            new_market.append(order)
            
        action["market"] = new_market
        action = _rank_sell_slots(obs, action, None)
        return action
        
    except Exception:
        farm = _farm(obs, _seat(obs))
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_get(farm, "hands", []) or [])],
            "market": [],
        }


import math
from scipy.optimize import linear_sum_assignment

SHED_TILES = [(4, 4), (5, 4), (4, 5), (5, 5)]

DAY0_PASTURES = [(4, 4), (4, 3), (4, 2), (3, 4)]
DAY0_MELONS = [
    (3, 3), (3, 2), (3, 1), (3, 0),
    (2, 3), (2, 2), (2, 1), (2, 0),
    (1, 3)
]
DAY0_WHEAT = [(1, 2), (1, 1), (1, 0), (0, 3), (0, 2)]

COMPACT_PASTURE_LAYOUT = [
    (4, 3), (4, 2), (4, 1),
    (5, 3), (5, 2), (5, 1),
    (3, 4), (3, 3), (3, 2),
    (2, 4), (2, 3), (2, 2),
    (6, 4), (6, 3), (6, 2),
]

WEIGHT_URGENT_WATER = 2000
WEIGHT_FEED_ANIMAL = 1600
WEIGHT_CARE_ANIMAL = 1400
WEIGHT_CLEAR_WEED = 1200
WEIGHT_WATER_PLANT = 1000
WEIGHT_HARVEST_LIVESTOCK = 950
WEIGHT_COLLECT_FERTILIZER = 900
WEIGHT_HARVEST_CROP = 850
WEIGHT_BUILD_STRUCTURE = 750
WEIGHT_PLACE_ANIMAL = 700
WEIGHT_PLANT_SEED = 650

def manhattan(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def get_move_toward(current, target):
    cx, cy = current
    tx, ty = target
    if cx < tx: return "EAST"
    if cx > tx: return "WEST"
    if cy < ty: return "SOUTH"
    if cy > ty: return "NORTH"
    return "PASS"

def v027_agent(obs):
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    day = obs["day"]
    hour = obs["hour"]
    
    money = me["money"]
    tiles = me["tiles"]
    unlocked_quads = me["unlocked_quadrants"]
    num_quads = len(unlocked_quads)
    shed = private["shed"]
    seeds = private["seeds"]
    inventories = private["inventories"]
    market = obs.get("market", {})
    market_prices = market.get("prices", {})
    
    all_units = [tuple(me["farmer"])] + [tuple(h) for h in me["hands"]]
    num_units = len(all_units)
    
    animals_on_board = []
    empty_structures = []
    plants_on_board = []
    weeds = []
    empty_unlocked_tiles = []
    
    num_cows = 0
    num_sheep = 0
    num_strawberries = 0
    num_wheat_plants = 0
    
    for r in range(10):
        for c in range(10):
            t = tiles[r][c]
            if t == "LOCKED":
                continue
            elif t is None:
                empty_unlocked_tiles.append((c, r))
            elif isinstance(t, dict):
                kind = t.get("kind")
                if kind == "WEED":
                    weeds.append((c, r))
                elif kind in ["COOP", "PASTURE"]:
                    an = t.get("animal")
                    if an:
                        fed = t.get("fed_today", False)
                        cared = t.get("cared_today", False)
                        fert = t.get("fertilizer_available", False)
                        yu = t.get("yield_units", 0)
                        animals_on_board.append((c, r, an, fed, cared, fert, yu))
                        if an == "COW": num_cows += 1
                        elif an == "SHEEP": num_sheep += 1
                    else:
                        empty_structures.append((c, r, kind))
                elif kind == "PLANT":
                    crop = t.get("crop")
                    wat = t.get("watered_today", False)
                    yu = t.get("yield_units", 0)
                    planted_day = t.get("planted_day", day)
                    age = day - planted_day
                    max_life = t.get("max_lifespan_step", 720)
                    unwat = t.get("consecutive_unwatered", 0)
                    plants_on_board.append((c, r, crop, wat, yu, age, max_life, unwat))
                    if crop == "STRAWBERRY": num_strawberries += 1
                    elif crop == "WHEAT": num_wheat_plants += 1

    num_animals = len(animals_on_board)
    market_orders = []
    current_wheat = shed.get("WHEAT", 0) + sum(inv.get("WHEAT", 0) for inv in inventories if isinstance(inv, dict))
    
    # -------------------------------------------------------------------------
    # 1. MACRO STRATEGY & MARKET ORDERS
    # -------------------------------------------------------------------------
    if day == 0 and hour == 0:
        # Phase 2 Causal Champion Opening: 2 Cows + 2 Sheep + 9 Melons + 5 Wheat + 5 Hires
        market_orders.append(["BUY_PRODUCT", "WHEAT", 4])
        for _ in range(5):
            market_orders.append(["HIRE"])
        market_orders.append(["BUY_ANIMAL", "COW", 2])
        market_orders.append(["BUY_ANIMAL", "SHEEP", 2])
        market_orders.append(["BUY_SEED", "MELON", 9])
        market_orders.append(["BUY_SEED", "WHEAT", 5])
        market_orders.append(["BUY_PRODUCT", "WHEAT", 4])
        
    elif day > 0:
        # STAGED LABOR SCALING (Hour 0)
        if hour == 0:
            if day < 3:
                target_hands = 5 # 6 workers
            elif day < 6:
                target_hands = 6 # 7 workers
            elif num_quads >= 2 and money >= 50:
                target_hands = 11 # 12 workers (Causally validated 85% win rate)
            else:
                target_hands = 6
                
            hires_today = me.get("hires_today", 0)
            if hires_today < target_hands and money >= 5:
                needed = min(target_hands - hires_today, 10)
                for _ in range(needed):
                    market_orders.append(["HIRE"])
                    
            fert_in_shed = shed.get("FERTILIZER", 0)
            if fert_in_shed > 0 and len(market_orders) < 10:
                market_orders.append(["SELL", "FERTILIZER", min(fert_in_shed, 10)])

        # CAPITAL EXPANSION & LAND (Hours 1, 6, 12, 18)
        if hour in [1, 6, 12, 18]:
            target_feed = num_animals * 3 + 8 if day >= 5 else 6
            if current_wheat < target_feed and money > 35:
                needed_wheat = target_feed - current_wheat
                while needed_wheat > 0 and len(market_orders) < 3:
                    buy_qty = min(needed_wheat, 10)
                    market_orders.append(["BUY_PRODUCT", "WHEAT", buy_qty])
                    needed_wheat -= buy_qty
                    
            # Quadrant Unlocks
            if "NE" not in unlocked_quads and money >= 1150 and day >= 6:
                market_orders.append(["BUY_LAND"])
                money -= 1000
            elif "SW" not in unlocked_quads and money >= 2300 and day >= 10:
                market_orders.append(["BUY_LAND"])
                money -= 2000
                
            # Calibrated Cow Capacity (Optimal: 8 Cows)
            cows_in_shed = shed.get("COW", 0)
            if day >= 3 and day <= 15 and (num_cows + cows_in_shed) < 8:
                while money >= 500 and (num_cows + cows_in_shed) < 8 and len(market_orders) < 8:
                    market_orders.append(["BUY_ANIMAL", "COW", 1])
                    money -= 400
                    cows_in_shed += 1
                    
            # Delayed Strawberry Powerhouse (Day 8-9 start, 40 capacity)
            straw_seeds = seeds.get("STRAWBERRY", 0)
            if day >= 8 and day <= 20 and money >= 250:
                if (num_strawberries + straw_seeds) < 40 and len(empty_unlocked_tiles) > 3:
                    buy_straw = min(10, 40 - (num_strawberries + straw_seeds))
                    market_orders.append(["BUY_SEED", "STRAWBERRY", buy_straw])

        # ADAPTIVE SHED PACING & SELLING
        total_in_shed = sum(cnt for item, cnt in shed.items() if item not in ["COW", "SHEEP"])
        urgency = total_in_shed >= 60
        
        for prod in ["STRAWBERRY", "MILK", "WOOL", "MELON", "FERTILIZER", "CARROT", "WHEAT", "EGG"]:
            if len(market_orders) >= 10:
                break
            p_count = shed.get(prod, 0)
            if p_count > 0:
                cur_price = market_prices.get(prod, 100)
                if urgency or day >= 27:
                    batch_size = 14 if day >= 27 else 12
                elif cur_price >= 80:
                    batch_size = 8
                else:
                    batch_size = 4
                sell_amt = min(p_count, batch_size)
                market_orders.append(["SELL", prod, sell_amt])

    # -------------------------------------------------------------------------
    # 2. TASK GENERATION & PRIORITIZATION
    # -------------------------------------------------------------------------
    tasks = []
    for (ax, ay, an, is_fed, is_cared, f_av, y_u) in animals_on_board:
        if not is_fed:
            tasks.append({"type": "FEED", "pos": (ax, ay), "weight": WEIGHT_FEED_ANIMAL, "animal": an})
        if not is_cared:
            tasks.append({"type": "CARE", "pos": (ax, ay), "weight": WEIGHT_CARE_ANIMAL, "animal": an})
        if y_u > 0:
            tasks.append({"type": "HARVEST_ANIMAL", "pos": (ax, ay), "weight": WEIGHT_HARVEST_LIVESTOCK, "animal": an})
        if f_av:
            tasks.append({"type": "COLLECT_FERTILIZER", "pos": (ax, ay), "weight": WEIGHT_COLLECT_FERTILIZER, "animal": an})
            
    for (px, py, crop, is_wat, y_u, age, max_life, unwat) in plants_on_board:
        is_ripe = (crop in ["WHEAT", "CARROT"] and age >= 2) or (crop == "MELON" and age >= 10) or (crop in ["STRAWBERRY", "TOMATO"] and y_u > 0)
        if is_ripe and y_u > 0:
            tasks.append({"type": "HARVEST_CROP", "pos": (px, py), "weight": WEIGHT_HARVEST_CROP, "crop": crop})
        elif not is_wat:
            tasks.append({"type": "WATER", "pos": (px, py), "weight": WEIGHT_URGENT_WATER if unwat >= 1 else WEIGHT_WATER_PLANT, "crop": crop})
            
    for (wx, wy) in weeds:
        tasks.append({"type": "DIG", "pos": (wx, wy), "weight": WEIGHT_CLEAR_WEED})
        
    for (sx, sy, skind) in empty_structures:
        target_animal = None
        if skind == "PASTURE":
            if shed.get("COW", 0) > 0 or any(inv.get("COW", 0) > 0 for inv in inventories if isinstance(inv, dict)):
                target_animal = "COW"
            elif shed.get("SHEEP", 0) > 0 or any(inv.get("SHEEP", 0) > 0 for inv in inventories if isinstance(inv, dict)):
                target_animal = "SHEEP"
        if target_animal:
            tasks.append({"type": "PLACE_ANIMAL", "pos": (sx, sy), "weight": WEIGHT_PLACE_ANIMAL, "animal": target_animal})
            
    if day == 0:
        for p in DAY0_PASTURES:
            if tiles[p[1]][p[0]] is None:
                tasks.append({"type": "BUILD_PASTURE", "pos": p, "weight": WEIGHT_BUILD_STRUCTURE})
    else:
        desired_pastures = min(12, num_cows + num_sheep + shed.get("COW", 0) + shed.get("SHEEP", 0) + 2)
        total_structures = len(animals_on_board) + len(empty_structures)
        if total_structures < desired_pastures:
            for p in COMPACT_PASTURE_LAYOUT:
                if total_structures >= desired_pastures:
                    break
                if p[0] >= 5 and "NE" not in unlocked_quads: continue
                if p[1] >= 5 and "SW" not in unlocked_quads: continue
                if tiles[p[1]][p[0]] is None:
                    tasks.append({"type": "BUILD_PASTURE", "pos": p, "weight": WEIGHT_BUILD_STRUCTURE})
                    total_structures += 1

    if day == 0:
        if seeds.get("MELON", 0) > 0:
            for p in DAY0_MELONS:
                if tiles[p[1]][p[0]] is None:
                    tasks.append({"type": "PLANT", "pos": p, "weight": WEIGHT_PLANT_SEED, "crop": "MELON"})
        if seeds.get("WHEAT", 0) > 0:
            for p in DAY0_WHEAT:
                if tiles[p[1]][p[0]] is None:
                    tasks.append({"type": "PLANT", "pos": p, "weight": WEIGHT_PLANT_SEED, "crop": "WHEAT"})
    else:
        avail_straw_seeds = seeds.get("STRAWBERRY", 0)
        avail_wheat_seeds = seeds.get("WHEAT", 0)
        pasture_set = set(COMPACT_PASTURE_LAYOUT)
        for ep in empty_unlocked_tiles:
            if ep in pasture_set:
                continue
            if avail_straw_seeds > 0:
                tasks.append({"type": "PLANT", "pos": ep, "weight": WEIGHT_PLANT_SEED, "crop": "STRAWBERRY"})
                avail_straw_seeds -= 1
            elif avail_wheat_seeds > 0:
                tasks.append({"type": "PLANT", "pos": ep, "weight": WEIGHT_PLANT_SEED, "crop": "WHEAT"})
                avail_wheat_seeds -= 1

    # -------------------------------------------------------------------------
    # 3. HUNGARIAN DISPATCH & MICRO EXECUTION
    # -------------------------------------------------------------------------
    unit_actions = ["PASS"] * num_units
    if not tasks:
        return {
            "farmer": unit_actions[0] if len(unit_actions) > 0 else ["PASS"],
            "hands": unit_actions[1:] if len(unit_actions) > 1 else [],
            "market": market_orders
        }
        
    cost_matrix = []
    for u_idx, u_pos in enumerate(all_units):
        u_inv = inventories[u_idx] if u_idx < len(inventories) and isinstance(inventories[u_idx], dict) else {}
        u_wheat = u_inv.get("WHEAT", 0)
        u_row = []
        for t in tasks:
            dist = manhattan(u_pos, t["pos"])
            w = t["weight"]
            
            # Distance penalty
            effective_cost = -w + (dist * 8)
            
            # Feed bonus if unit already carries wheat
            if t["type"] == "FEED":
                if u_wheat > 0:
                    effective_cost -= 150
                elif current_wheat == 0:
                    effective_cost += 3000 # Can't feed without wheat
                    
            # Animal placement check
            if t["type"] == "PLACE_ANIMAL":
                an = t.get("animal")
                if u_inv.get(an, 0) > 0:
                    effective_cost -= 200
                elif shed.get(an, 0) == 0:
                    effective_cost += 3000
                    
            u_row.append(effective_cost)
        cost_matrix.append(u_row)
        
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    
    assigned_tasks = {}
    for r_i, c_i in zip(row_ind, col_ind):
        assigned_tasks[r_i] = tasks[c_i]
        
    for u_idx in range(num_units):
        u_pos = all_units[u_idx]
        u_inv = inventories[u_idx] if u_idx < len(inventories) and isinstance(inventories[u_idx], dict) else {}
        
        # Check if unit needs to drop off heavy produce
        u_produce = sum(v for k, v in u_inv.items() if k not in ["COW", "SHEEP", "WHEAT"])
        if u_produce >= 8:
            # Move to shed to drop off
            closest_shed = min(SHED_TILES, key=lambda s: manhattan(u_pos, s))
            if u_pos in SHED_TILES:
                unit_actions[u_idx] = ["DROP"]
                continue
            else:
                unit_actions[u_idx] = [get_move_toward(u_pos, closest_shed)]
                continue
                
        if u_idx not in assigned_tasks:
            # Default to shed drop or PASS
            if u_produce > 0 and u_pos in SHED_TILES:
                unit_actions[u_idx] = ["DROP"]
            else:
                unit_actions[u_idx] = ["PASS"]
            continue
            
        t = assigned_tasks[u_idx]
        t_type = t["type"]
        t_pos = t["pos"]
        
        # Check prerequisites for FEED and PLACE_ANIMAL
        if t_type == "FEED" and u_inv.get("WHEAT", 0) == 0 and shed.get("WHEAT", 0) > 0:
            # Need to pick up wheat first
            if u_pos in SHED_TILES:
                unit_actions[u_idx] = ["PICKUP", "WHEAT", min(5, shed.get("WHEAT", 0))]
            else:
                closest_shed = min(SHED_TILES, key=lambda s: manhattan(u_pos, s))
                unit_actions[u_idx] = [get_move_toward(u_pos, closest_shed)]
            continue
            
        if t_type == "PLACE_ANIMAL":
            an = t.get("animal")
            if u_inv.get(an, 0) == 0 and shed.get(an, 0) > 0:
                if u_pos in SHED_TILES:
                    unit_actions[u_idx] = ["PICKUP", an, 1]
                else:
                    closest_shed = min(SHED_TILES, key=lambda s: manhattan(u_pos, s))
                    unit_actions[u_idx] = [get_move_toward(u_pos, closest_shed)]
                continue
                
        # Action execution at tile
        if u_pos == t_pos:
            if t_type == "FEED": unit_actions[u_idx] = ["FEED"]
            elif t_type == "CARE": unit_actions[u_idx] = ["CARE"]
            elif t_type in ["HARVEST_CROP", "HARVEST_ANIMAL"]: unit_actions[u_idx] = ["HARVEST"]
            elif t_type == "WATER": unit_actions[u_idx] = ["WATER"]
            elif t_type == "COLLECT_FERTILIZER": unit_actions[u_idx] = ["COLLECT_FERTILIZER"]
            elif t_type == "DIG": unit_actions[u_idx] = ["DIG"]
            elif t_type == "BUILD_PASTURE": unit_actions[u_idx] = ["BUILD_PASTURE"]
            elif t_type == "PLACE_ANIMAL": unit_actions[u_idx] = ["PLACE", t.get("animal"), 1]
            elif t_type == "PLANT": unit_actions[u_idx] = ["PLANT", t.get("crop")]
            else: unit_actions[u_idx] = ["PASS"]
        else:
            unit_actions[u_idx] = [get_move_toward(u_pos, t_pos)]

    return {
        "farmer": unit_actions[0] if len(unit_actions) > 0 else ["PASS"],
        "hands": unit_actions[1:] if len(unit_actions) > 1 else [],
        "market": market_orders
    }

import math

_MARKET_PARAMS = {
    "WHEAT": (25, 10000, 400, "sqrt", 0.8, "log", 0.2),
    "CARROT": (35, 10000, 450, "log", 0.2, "sqrt", 0.7),
    "TOMATO": (60, 10000, 200, "linear", 0.4, "sqrt", 0.6),
    "STRAWBERRY": (120, 10000, 100, "sqrt", 0.7, "linear", 1.6),
    "MELON": (250, 10000, 300, "log", 0.2, "sq", 3.6),
    "EGG": (50, 10000, 332, "linear", 0.4, "log", 0.2),
    "MILK": (160, 10000, 122, "sqrt", 0.6, "linear", 1.6),
    "WOOL": (200, 10000, 105, "log", 0.2, "sq", 3.2),
    "FERTILIZER": (100, 10000, 200, "linear", 0.4, "linear", 0.4),
}

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

_PRICE_FLOOR = 1
_DEMAND_ALPHA = 0.25

def _shape(name, value):
    value = max(0.0, float(value))
    if name == "linear": return value
    if name == "sq": return value * value
    if name == "sqrt": return math.sqrt(value)
    if name == "log": return math.log1p(value)
    if name == "log10": return math.log10(1.0 + value)
    raise ValueError(name)

def _market_price(item, inventory):
    base, equilibrium, scale, below_func, below_target, above_func, above_target = _MARKET_PARAMS[item]
    if inventory < equilibrium:
        amplitude = below_target * base / _shape(below_func, scale)
        price = base + amplitude * _shape(below_func, equilibrium - inventory)
    else:
        amplitude = above_target * base / _shape(above_func, scale)
        price = base - amplitude * _shape(above_func, inventory - equilibrium)
    return max(_PRICE_FLOOR, int(round(price)))

def _is_sell(order):
    if not isinstance(order, (list, tuple)) or len(order) < 3:
        return False
    return (order[0] in ["SELL", "BUY_PRODUCT"]) and (order[1] in _MARKET_PARAMS)

def _impact_score(obs, order):
    if not _is_sell(order):
        return float("-inf")
    item = str(order[1])
    try:
        quantity = max(0, int(order[2]))
    except (ValueError, TypeError):
        quantity = 0
        
    market = getattr(obs, "market", None)
    if market is None and isinstance(obs, dict):
        market = obs.get("market", {})
        
    inventory = getattr(market, "inventory", {}) if hasattr(market, "inventory") else (market.get("inventory", {}) if isinstance(market, dict) else {})
    prices = getattr(market, "prices", {}) if hasattr(market, "prices") else (market.get("prices", {}) if isinstance(market, dict) else {})
    
    current_inventory = int(inventory.get(item, 10000)) if hasattr(inventory, "get") else 10000
    
    if hasattr(prices, "get") and item in prices:
        current_quote = float(prices[item])
    else:
        current_quote = float(_market_price(item, current_inventory))
        
    if order[0] == "SELL":
        later_quote = float(_market_price(item, current_inventory + quantity))
        return float(quantity) * max(0.0, current_quote - later_quote)
    else: # BUY_PRODUCT
        later_quote = float(_market_price(item, current_inventory - quantity))
        return float(quantity) * max(0.0, later_quote - current_quote)

def _demand_per_day(obs, configuration, item):
    town = getattr(obs, "town", {}) if hasattr(obs, "town") else (obs.get("town", {}) if isinstance(obs, dict) else {})
    shops = getattr(town, "unlocked_shops", []) if hasattr(town, "unlocked_shops") else (town.get("unlocked_shops", []) if isinstance(town, dict) else [])
    
    turns_per_day = 24
    if configuration:
        turns_per_day = int(getattr(configuration, "turnsPerDay", 24) if hasattr(configuration, "turnsPerDay") else configuration.get("turnsPerDay", 24))
        
    shop_interval = 4
    if configuration:
        shop_interval = max(1, int(getattr(configuration, "townShopSellInterval", 4) if hasattr(configuration, "townShopSellInterval") else configuration.get("townShopSellInterval", 4)))
        
    demand = 0.0
    for shop in shops:
        products = _SHOP_PRODUCTS.get(shop, ())
        if item in products:
            demand += (turns_per_day / shop_interval) * (2 if len(products) == 1 else 1)
            
    if item != "FERTILIZER":
        center_interval = 24
        if configuration:
            center_interval = max(1, int(getattr(configuration, "townCenterSellInterval", 24) if hasattr(configuration, "townCenterSellInterval") else configuration.get("townCenterSellInterval", 24)))
            
        demand += (turns_per_day / center_interval) * 1
    return demand

def _order_score(obs, configuration, order):
    score = _impact_score(obs, order)
    if score <= 0 or not _is_sell(order):
        return score
    if order[0] == "BUY_PRODUCT":
        return score
        
    item = str(order[1])
    quantity = max(0, int(order[2]))
    
    market = getattr(obs, "market", None)
    if market is None and isinstance(obs, dict):
        market = obs.get("market", {})
        
    inventory = getattr(market, "inventory", {}) if hasattr(market, "inventory") else (market.get("inventory", {}) if isinstance(market, dict) else {})
    current_inventory = int(inventory.get(item, 10000)) if hasattr(inventory, "get") else 10000
    
    demand = max(0.25, _demand_per_day(obs, configuration, item))
    excess = max(0.0, current_inventory + quantity - 10000)
    urgency = min(1.0, (excess / demand) / 10.0)
    return score * (1.0 + _DEMAND_ALPHA * urgency)

def _rank_sell_slots(obs, action, configuration):
    try:
        market = list(action.get("market", []))
        rows = []
        for index, order in enumerate(market):
            if _is_sell(order):
                score = _order_score(obs, configuration, order)
                rows.append((score, -index, list(order)))
                
        if len(rows) < 2:
            return action
            
        rows.sort(reverse=True)
        ranked = iter(row[2] for row in rows)
        action["market"] = [next(ranked) if _is_sell(order) else order for order in market]
        return action
    except Exception as e:
        raise RuntimeError(f"MARKET IMPACT ORDERING CRASH: {str(e)}") from e

