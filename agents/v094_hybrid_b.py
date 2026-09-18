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
    'c%03hPp=(EZpFWfp|uwy%d$P$$<mux7>#A<&lnR!FbrgZ0KsJ8WEaeLkEEw}ySw^Fo<mk$Nh@E!tJ_`0VzJ1>L)I_<cke%b`~4q(|NY*-eDTY@pB}w@dGF1aU)=l8-~RjG|L5JG-u=%%e*68u{{Fx3{_mH2-@pFbuRpzb{^a%JSNGn2_45xmkKTQ_|MlB{_{+T?p1!!bXMB41lt({4{mY|g?;i5_`Oohj0pGm*;pXP2w;#T~eE0I^=E=Kn{&Mr|`HycuJUo4KH>8KVcfR@OmtPzw`t<RiU;lJ``8Mfa?)`l8^40B7w@;5B-3@>H^>Ki=;u}Tw^5)sI{lNYhPUb;4nXj@bToz%N#E;Kky!zpG#Ji7oYfMjwr*V4yom?s}{QmXRXHR~8`~R<AUqtD=>-4+QET27ke6wGx`~HhBzhy0X`}L2nwgnu=uqn)+-Yuv9+Pi;#(8x!xZeAp>*lDNpio1UvNb)kXTg@2WaFVkU<H@Y>8+LP?R~nk(?ghB7XH*5|xV<BnXHh+9W-p(=zFQKM;sW&`ZQsrC@~Rcuv7ZBo?n>IR8U5|`*V7JHo(r_Y7H3gSXj<DNP>SOWJBoN2?oR8IKX%q;e|(%)X<q#rf?KYBmr2|_npV1eJ|x4XCzlZ2^c#*p2))W!S=;OLF@JbF{LgNvv8h%+eE#g&&Er?U{^{n$tEbPN{@bl$fX5@AL$0nRD^yh&lz7bLK&=lw-YnCyYfR)~nXj;vAD-P%LhqM-Np_9G(l>tmp<efg8mYJoyLT#c1O?8J1OOY~dRBgc-?Vc%uJec(yvYP`zk@t%PM&9`DBz9I34CHW{BOMVJA(+*25Ix4W>1-&U(-1$c&P5MvcqR`V4H-jGvMOd%}5BP90;gCs#7Fs??h|B`(VF4#+~&0k{iOhiD}~EMhjyNSimH0E4v^bUlC>pvRQC=G~<8;2k;1c-#>lx^3{t+KYxGo;>F+I<K>^r$yyEw33lo49%sn@{0qnX_-Xw)UpSJjbN#AE{HoLb0+{U7z2W?Trnn*LfTc{oSGp1TiD}JaXP6`TEebXfZ?c|^A#m=1tT<lvlpt5p5*{uzXD2Z5o>nT{lwORl#-1d|I!``%U<GH4+@;OVkIAiuG1@(Bgj73Y+jh)|Hg|lV>mj>Er$y2W><BsE<t1{%+$lTd*rw;L|KzEYH^)EDE@m$hw_n%~^YpP$6|5j_oXybGlgIe}y~;j%@z+`gkTDHfjySd1dWAlei!#F3;Nyx(Qna`ykf1Z<J7X>P-e<Y4B~alogQ}c%KaSuA;=9x&mV*%!n>U9jwgbDq$dzydm$|$2c|^QeR&hwb$jxydI~@s@-*|l&D@1=bQYceN7g9fG!>_aV_0_0C+COU}EbJnAp>P^zTdwP>05$W#)H%>{t}qU6yeW0C#Pd?-EBRN}stQ``grrIR3X=AMX`8#}$(Vec-NC&bf485ecFgIy>S={-5#lyWxhkDAGhtmECEOmV0sT!<Ck!NH_VjJzH)7PahvlBrZrMsAfC2{LfK=9To!?UhyOg_QxB?GCQzp;XHE2~3yzodrOPAyjn0!>PgySz8$E#9ra%f6rp(<}Go#Zl6G}b`fH+fZ<AzGEbiz5C$AA&rx3C9VuOzrfT4JS?u)_2Bg$$jCeRh=t(T%;4$1E0Kj{!^?HMMsiGN1zNnY`5W_KY#b%+nPf>F1Dh>w<qosBVZmwSHmi((NYlqRd!_QfO>o7rj5lFNQ1B4^8u+GotEKI%16lKGpzrs>Z&-ET}`W6@h->V8je?t!Q9II!Jt07fVGrOvv%m)6ESz&Dxc#0<h$n!vWS=kEs=7<0iP?v4~NIO#`@^P&P6FI`{;h0K4>%7@5?W&uz01<Si;#vJu^e}eP=53B)<%W&F6@L42EJ$_0J4fq3SRd*Weu0y-BHvaAL9Lv^iSZa1LHf)j>yrDgEnU!XnX$dD@CLPB4aK?%!dB<&MX!{UBWjhb~a>DKH<odaUW>>XPTbhUk^x$)=CBB2=<-^~MoU+hVi!b98A#tqFK5tE?td3sI>>Z;n1gT8)9TeRCEu=q_>IS2&_g@18vU*Jx;s5#UVo#vRF0?AEU_7IhA(?^nFp{RF)dCUv1chH4quRino+Hri2Nqt;7+wMbC);0TRjWE=x^Lr9rVAop8^Oj&H53PIMiVtiOmNAai+r^2?n%fh?7a&!3TSEHQqc#wx#_&L09lNdN|{pc+L)-w+ybJk2nG7E^!!1cIJ7xkgB7)0g129XQBjVnIj#M1fn7dp;Q&RFAZq$vBGbs&#&MXgH_M+ZHQ-#f3BOB}k9=e-eVq!*T;GrfEHwl;tQcnT&mK;*bFf1u+uh?fVRnzrHn!Z9!<!$wLw&`snLQy18Pc6JhSb#B7iWj^xYn5Fs{72~uS)eO+}*UIiIMz26{jOjL`|4=?9^E@l<)8$$km!#P*ZM1Q_%MmY_V6-R-7_C#-Mc9W-bR5n7KfKYQhx2JkfcDj3lq&IAtyp~%$6ua4`*R1cHUf}RUQLfDr=+MDWTG~{LSErvkiK3a{e}*Y5tjJplo+Dx0rT*Da@E=31Aoh=Fa-rg6Xno7y3_786#J+=)Jhtm)TB+JweCz5yJsC4vbU4R=?$Zhmr`!ilI?@<BX4z3*;HAo@e{hHsH4|SzOlEAevJ`XduA5{9aab<uuo*#St8C7(H{#fFWQ(mb034Ca7D03-rwORA}+j6CFE{nXyZ6rKH#=ms%0*wWP+a}*CSlZMT(Ix)%3iVtFJTOQCmjp-goc+?M9(}zb!te5C=IX)fk7;;+WhL|4`OvY=Ynz@|&hu>B^OFGlA!s2rAc7-nEdNBB`yYl|lRyJQ^gKs8JOraP1@+%}yMmS>3`_W=B33Az%|RC5a(VTNWhIm>zktQkQVG@cs;c-Ky!@JiOhEfj~o8@nmqUBBJ$iGHajd)dbhk<o6|2vI7Y*e5zoH+n%-e92U;9aMTKq!V^oK^x8iT@fak)_VCwNvFWPu`B`6r)Ek5yI~8Nm)3i2l9s{|sU~ob3kN3<NoZB?1I{q&FLZxo=yNX0;y#t#+cwHaT03khRbEqw9&vqGL71gjZPw~N$z+Ul>&gw{}&802ndn8$-j$u=rg6;clCm{l(WN?K&Bha<_o>6XZYvSj<@=dxI&i7v)6lQ8iM3zr#xN_pq+Kg6s)!BeLOIDLu;lWHK*ysW=(onjs@=IGmoPuQclM_h!>2Au{bYW2AHgki>jxmcICBlp5s$f>Cu|jk-r~nC10WI-xPb-1#fl6ttKn@Z*nwSS7LNU5MFqu=6&P7~!>SB|1l=6I#IMh<XHn}>F-`CDHCDR`VeNC&QUHFx}P7_ouLYzGEDZDQpA!#N>^Qofohy|+I9I&R)^wCSl>rAao0I?)ho??UNSmm_{Fp=i3C?$|MjBx8`pwV25!_^Pi2N3!zh)sxcaqmu}kzmTu#Pe3`b(;l})LD1*TGAH)^%bL5^c@H4$#VdrJr*sRl5~gbBZ1Srvvw6CCvQ){JhTs00!0~&DEA2n5RG^r8r>Di3fEr=znt94C20kx#chVB*)P6_Hg#a_gt+}9EXefq8B3}@#YU#`pv5Lub}X1m9ONlAjHgzh^TyFU6WE*$n;0ay56O)^!>9D>Kt0-aAF%7hgL6`=zsqHNT}ez`irI{qKJi+QX8I$?`D26Lu#g1Pwm}!&N|?X>+k-RkRrck+1(TBBNd`ejV65p-V7Vf2=e_G077+QtC8aDT(YrL8E0ns3W3UBnOcgNj((BWwLcUs1922c{Erg@U;PT7E*)9ef>^R1m^R6>q-zokmMp<bJ9fgkpUp%LeR;x;AU*)yXSZCpO3mAo2CEZVTR1W2c1BwZ#jqM~mWf>AwmP76PxYE>8UzBVPDPW<R;<2sJ+h|K+=oT<Ef{nOdQS(h^X$gxrF4m8ohykjH1SSQ~5@1AAD^{qELICC?Q{%yQ6a>EQ`{58P#?XArv3r(9>OfAI$I$8wH>hwDj4@%88+(ov6I!kzY+fpm+a5YBzPrslgojrQh-1m6Gx2&0Qq?6!a2sA>6rI)+*g1U{gFKIv?ir{LbS4J>TrmS_N^gVg&x#(fqW?sh2=IQdv|2!jR&14zalmhNd~aX!<dXzGP3e*%*D2_t<R=rE%gl&QWcqU|y{QuBtp%#-cY)8MZ1!zIXqmM_CV<pY1OT?!_PakBb6bIBvw(EwfsoVL_*h_`mSoeggePBAZCE2W5YX*0ayE-fN39rGA=jUzbr+3GrHhMnad9x<5a@AvNlJeJnBtTWVLuyBSZhZ{2m*)<cl@`j2q|EzkUh9sFOVQ}QNkd?+e;R-ToA>u+aFzJX|%_X=?J5?(`Xf0zW~NF`+5F9w-))|u9Zo5-`|Wj6>Xki1^V0KJMKS(R;EMfb|q1*7e9xfmYj_h9Y@k!I6DRT)Q6=qV+thl!-z17&~?Ps<P2$3d_8>R(zKddl+KF6jb=1xfwz^S;VWHhMx$;=51GFlnVf?X{;?X|%N$(eAM_<pJMTcerA+%#rxjDBnkx`HO=M?PZhm<_j`owou*F1C--~5zJ<RhQb5A6nVg*Up-vymy+G?I3!eCZ44`>G|a<`f>fg`zcT>@hhv_qI>QR7z?Dh`}T*GoS6qXScn_NugZgBpdyp1LMZ5M4#ktb<r})tl(4irPljvtQpO$`fc0IJtRmKolc0UB0ppX!Iu@y1Akzwtzt^=$nB}x3itLFn2Gb#{Y__pXM~@F0{gGfo>zyXow$Ts{2P+qdxHQ`Bx=?yK>7xuJ~`Zf!oXM0~GY#Fa@2$ouIQ*7}BS+V`?oVuM3Tedl>-KBH8Ta()IXzD~8DF=&~?9=-4)ut1j@+IqZ{k`RL!)j{S!RwLd6LD}yO`dw#ddCDm`XhtMuGo_4Ydo5}Db3}&iUmj3>t)sNb4Do*glCtJAH(kAkur&!43PBDD*`t_s220;P*SqxCn&;?Cbw%b6ma=G+GG~diKyecK%$fgPeoBOd9u8s^k+|;@Q(8kau0i=ylx4QB=>fNBESYR|rgm(_HmPf-uYFo4-Zx$33k-Hecj8GJQwrh1F{Z@fbh{eZ3fAMVE*#i7qa08~=8m0Cgl81E)N%|erb{{u|vuXZTsGig3-E`9m(7?@^m+<c3xK#oA45&6fOI+8$mxkw`7LZJQS*!sQ;(OK$cgw6ux2M5+y~SJ*p^s7j5Q#-QN~g^qx_DP4bZB`i+#dsusN2r;$Xt<LHv#axa=pU>n4Hj55|iK4q6LU)=)^?tM$h6!mTl_5A^ZvRslsvaqgvr{9?C2zdx4&Zx7AcDa?jPz3kOslHE@zerGAA?x}cj3irVKUpspBER{<JXQ8A-4K!V($%z<d+>#17~V}$M2EBuE@XAj#?&`?T&C`5RiLB7fMhXg%T-xc0e!Z1!PS7feq;f};NRQ-mjZ7PwUu81IK1nG$Q)QPm)qY~xyI|~RMlCqEri%&W+Crk!JBF2-iL<UhrxDs;;-E#m1)EtE^(5w=M+CqC5lhn!F88xT4$xy?L0u6)1gDT7Sqt4_e=$gYy*9N0$iAcf~sU_3p!L0ry2M(knQmWuFJD6lXa0v!6j|~1{JPBG1(RATp8SdYL17l%6MD2oyksef3<gtL@=aV|ds)ADWdVa^SMH;GnT5wVC^(Z?F3TON)Ga_Iwq~~0-Ze~R{h*AZOSmR~QAoAe}v_+LS*rpvjKj^@#Oa$%6v?NhM63uB0VyL3+L*TzuE}l(NQqg*Mv2<5kOWiD3eMH7=!utRxQE}166yqpYKXzZCx#aQ~+4*iSi0x`fZ;Ez`*V6dH%_9A_WJ#?^BydS6^b)<4!N(!;?4xC`Rq`y6p$I+l9uJjfZWUehN2*);2_B*F*N?d`pjBd|i?27<8PBm`vXwx??)@S6JMF2CgsbQ%eX4DoiWsYWEQ7i!8YJ$c=NW{;U`eBCrqy)z^k^5&!WF~6aM4#G&UUT{9Zf++rs!&ry}P&+_wE@3)DW_g?!i=;M_)77*kQlMZ6}f+St!G|4wT>-&#}<t6V}wM<?pO4knv*myg&xMxRh6uMABk^1>F64&Y%dV%9Iehi(kp!PmZz_JEi)LvK7`{w)0*({C4PvQ`2=TPQC+Ou4&GcUxTgT<3h3XL^8K>IZIT`BJczbGRGk|HnC!I1?Oi})}i}EOowHaavjAIs^BFuAq`8gc8d#mDRZV`+f}H>NIC&e(9eu*9Bmpa6?@uGebXdptFkad6^EIe2eHjX5eI5CH*`-Yldx?25^i3+5*n-$lw~oo`eZV(xcSu;UV+kXDf??+*UG6|PAXhQNhBE44`6eAG|2#MB6L){;bRyjbj22T0Myv6v}3kIB<l}REO3WZ(_RN=Cg_f=d_lOqJjC{;K?T5>=hTiJ;~|gLh|%J%Rgx1BJgB6UD;f%uRm@vV8^;$R6M<S#SC`r+u^X%u_xOyDj@x{ix~qk}i?oU7Oi7injcLVESRyrSZpEE2`=sQk%l`B<;VG4?7S%Wtq>EH-5fUnKwe5jlqZmr}iV%(U^s$FdSN=0GFPmFZYEH?kbGh+e;VrWJ#B8({RIo<{P^GG_yk!N)*%!&U%O)xcgSaNInhHVWFf>YfN<=Gng;uGOz>;@}krgT+Au%Vcv)3``Al*`8o_DG$o=P`axrL~3Ysu4(61<e8%nW0&GUs^lE4Y3X=cR0vVGn7Vs)%j(@nRIFLwTGaBU1-y`;~{P)-x}?l&c3N?m<t3`r?w(3ZF#w!2(%k`V>t&sbHp9u6u6d!H^qGR^GI2m#MxKxaKfgB6F}k#@SZ@0QDLki!9u*+|r|xOQveeG^1_CrPK-P2^u1L{ju2Eu8LZz9P1AbxX646z;9v3Nv@Z0C~WhQu%U$^nOvCIiI6;K-tu8V79JdZTAvZ}HjO}1yLbHhG^55e1js1fTQ8RytIRyx3>R){M2}foe|WQZQ4YOv>zEo>TxiT~;_|Jz%B(d_n!bkh_zdqol8~W91<l`zeOF0JYoN*JkcqFW)axABP`zH&&8!0KtbmFZI~9nZCA=dKqj&o?M>uqbTnb^v`HRk_S_!a`!`JwMa7)}C!{M^uJbV7*dsAO-{aJ7bdvrG6IrGR3ZXqANjCN|!*;HN8<5M^qi<Ubx0edM;0*h`MVdxn;<O?a6{Tv4q(N^?G!$0nr`XEl!nA{P(Qvr<634IU|n*+8EbK)QizaMQ{wP9ob60PiDPfpu_R~=wA<D#)38oOCc4i$_nRiR^#YBO!u{#`WG#;-N9l1F7YHKn>C{<5U-F2#;JCMT%>akNzO{=@PrOIMAO5MRq|_b^CAkYEaxTJbE;1CvzA7<-q+-8z-d^INCN1!{2cPlXpZ3^np4%NlF4;wbScj_82DMX4v5G1GDFSx3Y&VkZK%^D0*~2nQmJNT}x00t)gzebLI~UA77-g*_0zyLo=dJGzyrNW(-20(1=Rnn8$=75|DT4rIdj@*2;2Xuc&ToK~qG#~#F6!4r<kkd{M_VUIo+_LDzeC`ERsbu%49zTdIjZ_&PW?8gZtRuP?NQCBZTRH?;%{QTz&QIe0=k8@Yu>C%zmQ=}mS*TD76qDe_iaWNTloYtz&Owvm-+6PtXnZo$z=#1e5s?udaZ7@j==i4W)($XoISzymm>zq94dsdQI7{xatu^I&gR)6n!H4{dlm`||frN36IN0pBY(4rM+ZDkZ9aI{lOkpZrC_8^co?s%V0c=s<a+&dAyB-Fg?ZhKS($B~QtTYq=Wq=N7S&>bRjPBrn$BQ12y7ez?lzkd4c$**sHuvf2BYG9!PGM^M`XwhzAu<-U7k8egtEz$}jb(h21m$jKFqrH0>+phd%j`#o?w9c2uEK%T_r#iPo-;eE{f+P40<d5>`oF*gZ`4o*r@USdcFoh`^2dHc$rITTZUR^fL;E<imM3NQZi1)}$x?3jVDZp79s0=KgL?py<W8M2|>mckoYM)r4W<)Bvt$m>^-e4R~CwDa~SH%V*qCi(3KDC?RX;AcMd2Z!3C>tP2lW7l}8q1Zc%Ov2KGd%O$_t;f*zgZ5pgLX_0cYAPag|1L&?6Oa<NqW5Qy^`q#kJDw*W!$E5YE}q$R;5h_rZu*!D99Cz06i|w2rQ-P2oQ|4-=G7E2!4tS$Yoe<29W|)MOx;tsi5ykUNx=wAr3;qcw`OXB~Q=9ePwVU8r8X2*3|aoZnKa=j?(UKt>x4fWcihDXF%?H>_D3eV)osSs|KSgIq8Mz^*Es)VnKYwS>~s6v5#(JXI$>pzfpKAK%#yvn@~RK_)GA>+w~|kQw>Yyu42_s`Vk!$7vt*IAItMq29E@9luOP&SUsaTV=ccC;V&~|wW(s!k(%Eg;RoiOjU`Shd1mEdt0%yUZI8mt%Ei4{SJ)6JD5>Z`76<RganZlC9NSzM3%$u04<PUT^v8}Gy8Yb6u;P$8GLUzm8zJ4zM)-3ao$b>C2w~NYcKy=OxI^P|h~eR=7gdNMc<wjDmds-btJXqnk!APh2|qIbn-5+9Yp|UmM?52If}zl$3IbxXdp_y~eH!sl|CRt0Wu#pg!9a`gOjIxk|I>5AJe*PhnE-LsCZGh6mFNCf9BV<PF9z6Wc03s9GN&a90aY(I0m_8g?+W4L<CGQ}1-uc{MNBK&yQ9V*MW;%EO~!K0!sk)yfHo`tP{~`7ku68@NIuD-52DeCq_8Rk!9RkUcw4#(qr~7usaix;<rVNvGkT~X_rW%zc)M_O%<=mIN5`h8(bDnRc#&R#-6bk~L@(4uRtDEG(oQt3l`B<^{G3~pC>m{;`>=HF0~w!*?h(qE8#ZX@>2BtsaypJGGv|%S#3OosZfGX$YBdufQbl%ErHb{Y%uu>T6(qbbRF94tL;tkqx*brUTl&nBW0|9cLE|i<V}$T7V6Ij{ICOzR>#}jq0ikrc={ObPIGsA0w2ZCmv0?v|5;u^hh~J<7rI;8(<aw8boIZr3qTQQ=iGr<gWO!OJ=J=>jh@+BV;=gqUK2^?Wfuaw_1EE^sNNxzm@Oimkr;UX0*y3|S{jy3I>eL?w5r^HpIC|9e3K0G4MEUoLf1*a)#$Y1HUS|e5;`Lk4sgo$zZQ;vl*C7H>6cUl^k>lA18@GU%%Bl~EmlQa1aOmU(6Xb=*rpD+^sXW`xR@O>Qu?AsW`6mZ{9+$!Gj375X`k10kRB#TM!DXaTcUfX+aYY+F?uh2}M6Q5tJTEhP?<7Wemx`L3B7?VDg=cdy`6KNLrzLuCHy8Ms8D{Pj)CNIFTENuV++bokzSOAKuD(oNfh-|dgght0W6B2PVPvlzUtY*?GD^p~n8Ti?YmX^H4q<R3#iIclHW{Z5iqSO3{^i#8SA7fwOT(&5A1z(OO6eRBT2_RuYXEj6?d&!p>J~(Tylmoajp>uZp{qj%(g~u_!E)wXIj71Xn=kIq5Y6NWQIfNf<68m;a_1mgdkA|(RAWu0>od#-T(=ksf0}DZ-+eN{=MGKoR56#~KM^PHfjXDQ!>o%0+5DRx-A(bvi=(w!F`CF$7;fU{tMRVr<RaK=eg9s;5pISirK>UPu2ANrK*`(zZK%JLVW~)4E(0A^t1te96Gv3)rOuWygH~ej;o)pK+QMbP2A<P+WEa>a5*4t~j$_v5Tb4*IgIZzjRCcRk8!`fvNJ=PqtD2Aa8+;V$e0Z7chAv~iFAb2&<;Ym>aAIX_4GU0dwbR5sqB?!Fj3Y&^Us}vlx!cu;Bt&Srg#9Eze*@l@E0c_Q_bAT<(lw`P3Pdql4TnjA-;H`TLHb}_MxYe6ME)KSyGZ^+0nQ|=P9eEymYwVmt8Z`n?@!sdYAUdEc`t+G;t3qdtvHZrFrkgJ)=jX^#CfBrv3b#Yps2S^ZsO%F+<ck?J-F$Nh$csc3;;A2#s!h~u3zA4)VvH?fL+>&E-a^cjf6YQnNK6}PV6mBt2+7fbB(VotT?Ymy?%x2LTqh)m#b4xc44M%L?}>hK+6e<DDkQUzE-K9sMPdX?cZA6v;5`Q*yRqS^(otF6?pdI46RMjbfT}@hRa@0_F$KAztG<hahLR5<{|@yLFNvnWLP+C3WYbGk1X?6Of^mdw4<@-ut!dRZ?UG{4~AXMPt*Dfs2aGbyo$(hiEr75?oEj$I@}J8lcvUI>t>Ln*n0v}l(?neDoUg56C*yHq`}RE@)~Sqf7xP8Kv8N5=>Q!&@;OE=R-|YP6e)-5P^q4jGUBII?QHsbJ7}C=pyp(*U~!o$)=mf*_a8?1KBXU3kyOe0vEj`zi*Aja0$DW44^5hihpI^(@)~mRTUUw+CU(dvYZG1t-fdj?!=<#ia9|9n2&y=6AH7c#*0?x3oFS}Dj7;${8DP4d`_WRrIl+U=*=PuJo&FfjrxQGjNU}P#qgY(%XQD;hhvW2^%!bVWXVLGy1AyV2zO9a0*B^@hJ-bs&)6%kk9F-+L7=G!6<dteenoO^u`uU@0V$4?91?F2jqbfRQD0?qMQb}*ZLm?WK?nLE{8@;;9og~sT6~&fQS}pk~1mZ-8{?x_wee@~efgk_o++^sk+PWehqj#B#*nDtrdxRLbs8y5H(+XiPjqt@dk*J`_q~v6<Kymji(Ap>jh!UI?n0f;1UZ>X>Z%L)iYfST^<~PBK`2iwq;3Kk-U6nE`c8>rz6}LqnK1RWM`|2jqZd_;(j$QMf3T(*0uGEbTWvB(q82jyPJ}k9ai60oLM^Z*ZF-6X=a<zg?r@mp6JTEb=BmlGOhMc^Tpt)eN7T#(JirG*q5$RLdmk*ZxJ1b{K<}xqqbE=MWh-}{pjJ-{twQ#(p^zIBWFNvhV<@I0G1}R@JFN2bc+#Ow>rm#l`#h)|x>0P4zZ{n@q!CIEK!(TxxnsT2M6T!G0I73hFrw>_C>Y$_HC{!^6W-+{yu=9b|z!AaS7Q-e2q0$8jjFbvxYTRqHL3HFoYHUVv%5q1xA?-r7POUJ~Wh}4K5OjDHaUlC%3=C6zy8n?8UARS+9m%=akE$eVhTq{SdDmYnJR|KSt8HVOP+2h}j?uRY`jiDsX$O5?fh_9UH#Z#{mK=v;6wP`2AHgri<4R>lPRo5S`z%l1pm1H7Ta;x1Mhtz;YR4EwuA&WRb^fhFj3Td`5j+w_$h+Wpy;jWYLN<q+*n;XXpn=+LgDxdhp@F44sUR*Bl`<;Nf8>KfJXwf-%ei`mjt4a|ycbT1f1$m(FlRm`Jpe5^Qmw67uabYtgU<1j+GKzY=Q8aMq%ut7TvhXWctmj)vM}gV`)UG_z=)5AasF~d71UfDoiwVXJEL0L+~JgHfDmhcU{M*Y@PI3RXnZ1-H-uY4EK(m%!|VL`KK9Z}$_v10s!(W@9HqJ_D#STm0;joZ)?xU`yxa7YycCZ+W`kr}thN#4f{t0J>?lRy&UZ-9Hbg>HX~cL!6O`iy$ir_l@Kyn0G)8LCudGdF9amz6Vw;P~x_)2NIl1B<vboSCH)|ngc8~$`YPqW4<xglREAJb6p@INn@rz+0q@(;GRpmfw<#MKv*zASTO2(Lhig7vh`^iP4R}KEv43NQ)H><^;oPHe*csua-9@ix)=Pp7%upQU}-y$XMR3M@BW$+o3f}p!MtAILBvFCRa?enEpME#%~QoDh4{)=&uEXC$lgur!BRS<9f`R4xtY4W%#')).decode("utf-8"))

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
