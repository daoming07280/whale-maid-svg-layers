from pathlib import Path
from PIL import Image
import numpy as np
from scipy import ndimage
import json

ROOT=Path(__file__).parent
SRC=ROOT/'reference.png'
if not SRC.exists():SRC=ROOT.parent/'upload/01-1000012597.png'
im=Image.open(SRC).convert('RGB'); a=np.asarray(im); h,w=a.shape[:2]
bright=(a.min(2)>230)&((a.max(2).astype(int)-a.min(2))<35)
seed=np.zeros((h,w),bool);seed[0,:]=bright[0,:];seed[-1,:]=bright[-1,:];seed[:,0]=bright[:,0];seed[:,-1]=bright[:,-1]
bg=ndimage.binary_propagation(seed,mask=bright)
# Enclosed background gaps between locks and inside the tail curl.
bright_labels,bright_count=ndimage.label(bright)
for i,slices in enumerate(ndimage.find_objects(bright_labels),1):
    if slices is None: continue
    ys,xs=slices
    hair_gap=(xs.stop<351 and ys.start>279 and ys.stop<464) or (xs.stop<291 and ys.start>549 and ys.stop<876) or (xs.start>934 and ys.start>549 and ys.stop<851)
    tail_gap=xs.start>880 and ys.start>950 and ys.stop<1140
    if hair_gap or tail_gap: bg|=bright_labels==i
neutral=(a.max(2).astype(int)-a.min(2))<28
bg[1410:]|=neutral[1410:]&(a.min(2)[1410:]>160)
fg=~bg
lab,n=ndimage.label(fg);size=np.bincount(lab.ravel());size[0]=0
fg=lab==size.argmax()
# Remove the disconnected floor shadow; keep white lace enclosed by the outline.
rgba=np.dstack([a,np.uint8(fg)*255]);Image.fromarray(rgba).save(ROOT/'source-transparent.png')
im.save(ROOT/'reference.png')

parts=[]
def add(name,label,path,z,cond='',under='',role=''):
    parts.append(dict(name=name,label=label,path=path,z=z,condition=cond,underpaint=under,role=role))
def poly(points): return 'M'+' L'.join(f'{x} {y}' for x,y in points)+'Z'
def ellipse(cx,cy,rx,ry):return f'M{cx-rx} {cy}a{rx} {ry} 0 1 0 {rx*2} 0a{rx} {ry} 0 1 0 {-rx*2} 0'

# Painting priority separates visible pixels. z is independent, bottom-to-top.
add('back-hair-r','后发·角色右（画面左）','M0 0H608V1536H0Z',10,role='hair')
add('back-hair-l','后发·角色左（画面右）','M608 0H1229V1536H608Z',11,role='hair')
add('tail','鲸尾',poly([(702,1070),(892,1022),(929,968),(1026,995),(1097,939),(1215,851),(1229,1370),(671,1325)]),0,
    under='<path d="M730 1080 C815 1132 886 1111 944 1032 C964 1005 991 1017 989 1052 C963 1150 876 1222 761 1192Z" fill="#3d5598" stroke="#27315c" stroke-width="3"/>',role='tail')
add('leg-r','腿·角色右',poly([(424,1100),(576,1120),(557,1285),(518,1365),(418,1334)]),15,
    under='<path d="M467 1110 C515 1103 558 1124 558 1169 L537 1290 Q496 1340 444 1285 Q422 1218 467 1110Z" fill="url(#skin-fill)"/>',role='leg')
add('leg-l','腿·角色左',poly([(614,1123),(749,1090),(781,1294),(750,1360),(659,1363)]),16,
    under='<path d="M635 1125 Q693 1105 728 1147 Q774 1225 750 1300 Q705 1337 659 1299Z" fill="url(#skin-fill)"/>',role='leg')
add('shoe-r','鞋·角色右',poly([(405,1325),(575,1325),(576,1506),(399,1506)]),20,role='shoe')
add('shoe-l','鞋·角色左',poly([(627,1326),(792,1326),(797,1501),(620,1501)]),21,role='shoe')
add('sock-r','袜口·角色右','M412 1260 Q483 1307 553 1267 L552 1313 Q534 1336 543 1350 Q508 1381 438 1350Z',22,role='sock')
add('sock-l','袜口·角色左','M643 1268 Q703 1306 774 1261 L779 1319 Q763 1334 759 1352 Q704 1370 660 1355Z',23,role='sock')
add('sock-bow-r','袜饰·角色右',poly([(406,1281),(454,1283),(470,1321),(447,1359),(414,1350)]),24,role='accessory')
add('sock-bow-l','袜饰·角色左',poly([(750,1281),(789,1280),(801,1350),(764,1360),(737,1322)]),25,role='accessory')
add('skirt','裙身','M505 786 Q601 773 694 799 C747 850 844 934 923 1027 L914 1101 Q614 1290 274 1111 L262 1028 C355 939 438 855 505 786Z',30,role='skirt')
add('skirt-hem','裙摆花边','M260 999 C365 1139 474 1156 597 1159 C765 1157 862 1091 918 1006 L951 1053 L899 1134 C791 1235 425 1247 273 1086Z',31,role='frill')
add('neck','脖颈','M544 561H657V676H536Z',40,
    under='<path d="M565 585 L636 585 L634 650 Q604 682 570 650Z" fill="url(#skin-fill)"/>',role='neck')
add('topwear','上身服装','M479 613 Q597 592 713 614 Q771 681 728 800 Q605 871 468 798 Q426 699 479 613Z',41,role='torso')
add('sleeve-r','蓬袖·角色右','M467 645 C436 668 391 706 392 750 Q400 807 451 831 L489 794 Q489 717 522 653Z',42,role='upper_arm')
add('sleeve-l','蓬袖·角色左','M702 643 C762 674 805 704 797 750 Q793 800 749 833 L707 798 Q717 718 674 657Z',43,role='upper_arm')
add('sleeve-frill-r','袖边·角色右','M375 775 Q415 769 451 802 L465 835 L436 850 L390 816Z',46,role='frill')
add('sleeve-frill-l','袖边·角色左','M741 796 Q777 771 814 779 L810 813 L760 850 L728 838Z',47,role='frill')
add('forearm-r','小臂袖·角色右','M382 794 L447 834 L390 917 L314 884 L310 851Z',44,
    under='<path d="M390 800 L438 830 L385 908 L328 880Z" fill="#2f416f"/>',role='forearm')
add('forearm-l','小臂袖·角色左','M805 794 L871 848 L889 885 L812 920 L751 837Z',45,
    under='<path d="M803 800 L763 832 L814 908 L873 880Z" fill="#2f416f"/>',role='forearm')
add('hand-r','手·角色右','M230 872 Q275 875 315 858 L356 889 L327 941 L230 954Z',48,
    under='<path d="M292 890 L332 865 L350 888 L324 919Z" fill="#ffe4d6"/>',role='hand')
add('hand-l','手·角色左','M844 861 L892 868 L952 883 L955 957 L851 948 L821 892Z',49,
    under='<path d="M848 868 L890 890 L873 923 L826 895Z" fill="#ffe4d6"/>',role='hand')
add('cuff-r','手腕花边·角色右','M288 864 Q300 854 316 861 Q349 875 364 904 Q363 928 344 939 L329 924 L321 908 L307 895 L302 882Z',50,role='cuff')
add('cuff-l','手腕花边·角色左','M878 861 Q899 864 895 879 L885 885 L876 903 L866 914 L848 940 Q829 932 824 910 Q844 874 878 861Z',51,role='cuff')
add('waist','腰封','M486 769 Q595 777 705 770 L698 825 Q591 849 498 827Z',53,role='belt')
add('apron-frill','围裙外花边','M498 812 Q600 850 695 816 C724 839 736 870 738 907 Q779 991 721 1047 Q659 1096 550 1061 Q442 1047 448 960 Q455 868 498 812Z',54,role='frill')
add('apron','围裙主体','M510 830 Q599 852 686 831 C697 858 716 910 716 955 Q724 1003 675 1024 Q592 1047 535 1015 Q466 991 475 939 Q487 861 510 830Z',55,role='apron')
add('whale-emblem','围裙鲸鱼图案',poly([(607,911),(711,911),(714,1007),(607,1011)]),56,cond='blue',role='emblem')
add('skirt-bow-r','裙饰蝴蝶结·角色右','M389 972 Q406 984 417 997 Q446 989 453 1005 L443 1050 L437 1110 L386 1122 L357 1081 L383 1031 L373 1002Z',57,role='accessory')
add('skirt-bow-l','裙饰蝴蝶结·角色左','M801 973 L822 1006 L810 1033 L846 1087 L806 1115 L767 1113 L747 1029 L748 1000 L778 990Z',58,role='accessory')
add('bodice-frill-r','胸前花边·角色右','M467 610 Q495 609 532 644 L511 766 Q474 777 459 732 Q447 663 467 610Z',59,role='frill')
add('bodice-frill-l','胸前花边·角色左','M681 632 Q704 615 723 611 Q750 663 732 733 Q723 769 690 766 L661 653Z',60,role='frill')
add('bodice','胸前衬衣','M541 635 Q596 614 650 636 Q679 679 686 739 L675 773 L520 773 Q496 747 517 685Z',61,role='bodice')
add('chest-bow','领结','M534 625 Q563 621 596 639 Q631 616 662 632 L666 677 L645 683 L660 709 L628 724 L598 682 L570 723 L535 707 L548 679 L530 677Z',62,role='accessory')
add('chest-gem','领结宝石','M597 632 L618 654 L598 679 L579 654Z',63,role='accessory')

# Face footprint is restricted to skin/warm neutrals. Blue bangs stay hair.
add('face','脸底','M430 311 C497 246 695 255 754 350 Q808 470 772 553 Q742 599 614 618 Q481 614 434 568 Q395 510 430 311Z',70,cond='notblue',
    under='<path d="M456 348 C463 276 698 266 743 349 Q786 421 766 526 Q743 596 606 614 Q468 607 435 542 Q405 446 456 348Z" fill="url(#face-fill)"/>',role='face')
add('ears-r','鳍耳·角色右','M340 365 C296 412 200 476 146 495 Q133 519 191 523 Q238 542 291 520 L357 490Z',66,
    under='<path d="M333 392 L386 400 L365 484 L306 499Z" fill="#535a99"/>',role='ear')
add('ears-l','鳍耳·角色左','M856 365 Q946 454 1066 490 Q1086 515 1024 523 Q964 538 906 514 L848 493Z',67,
    under='<path d="M872 384 L819 399 L844 487 L908 502Z" fill="#545b98"/>',role='ear')
add('eyewhite-r','眼白·角色右','M432 474 C439 441 463 421 490 424 C533 422 548 458 539 495 Q528 526 489 521 Q443 517 432 474Z',74,role='eye')
add('eyewhite-l','眼白·角色左','M652 474 C653 439 676 422 704 424 C743 423 763 447 767 473 Q762 515 715 521 Q665 522 652 474Z',75,role='eye')
add('irides-r','虹膜·角色右',ellipse(500,478,38.5,42),76,role='iris')
add('irides-l','虹膜·角色左',ellipse(695,477,39,42),77,role='iris')
add('eyelash-r','上睫毛·角色右','M420 460 L424 442 L435 440 L437 422 L450 429 L455 411 L465 421 Q509 403 537 440 L543 453 L533 452 Q513 431 488 434 Q451 436 434 478 L426 498 L420 483Z',78,cond='dark',role='eyelash')
add('eyelash-l','上睫毛·角色左','M648 450 Q671 409 716 414 L736 423 L741 416 L747 429 L758 435 L759 445 L771 456 L777 480 L766 499 L757 472 Q743 437 704 432 Q670 431 654 455Z',79,cond='dark',role='eyelash')
add('eyebrow-r','眉·角色右','M466 339 Q502 330 532 349 L531 360 Q500 345 466 366Z',80,cond='dark',role='brow')
add('eyebrow-l','眉·角色左','M654 339 Q704 331 731 359 L729 367 Q692 349 654 359Z',81,cond='dark',role='brow')
add('mouth-open','嘴·张口','M568 533 Q596 524 626 532 L634 558 Q628 591 596 592 Q565 586 565 555Z',82,role='mouth')

# Flowing foreground locks have their own roots and hidden overlap reserves.
add('front-curl-r','前侧卷发·角色右','M339 501 Q393 497 419 549 Q484 632 438 695 Q411 707 401 751 Q369 775 340 745 Q317 722 334 692 L333 660 Q369 677 366 644 Q307 608 339 501Z',84,
    under='<path d="M343 514 Q376 484 414 522 L421 582 L346 595Z" fill="#497cb8"/>',role='hair')
add('front-curl-l','前侧卷发·角色左','M792 499 Q843 508 853 559 Q880 618 836 651 Q818 668 857 661 Q856 681 830 687 Q877 723 850 754 Q819 776 794 744 Q791 704 766 693 Q714 641 757 554Z',85,
    under='<path d="M770 516 Q805 489 842 530 L845 587 L758 585Z" fill="#487db8"/>',role='hair')
add('head-frill','女仆头饰花边','M345 298 Q363 209 422 168 Q459 120 508 101 Q558 77 610 92 Q673 75 728 115 Q790 124 827 202 Q866 237 872 307 L826 321 Q771 166 607 157 Q445 164 391 316Z',86,role='headwear')
add('headband','头箍内圈','M373 287 Q425 146 578 135 Q756 118 836 278 L846 324 L825 318 Q761 155 608 153 Q454 155 392 309Z',87,role='headwear')
add('bang-r-outer','外侧刘海·角色右','M442 221 C384 255 336 321 308 421 Q301 503 359 547 Q395 565 457 548 Q414 531 417 503 Q385 405 470 291Z',89,role='hair')
add('bang-l-outer','外侧刘海·角色左','M722 219 Q836 263 858 364 Q887 475 835 526 Q814 562 733 568 Q761 545 753 520 Q779 470 748 414 L699 279Z',90,role='hair')
add('bang-r','刘海·角色右','M592 172 C544 129 472 160 421 209 Q367 284 335 392 Q314 467 350 526 Q394 569 453 545 Q412 523 423 460 Q447 367 491 333 Q533 286 559 237Z',91,role='hair')
add('bang-l','刘海·角色左','M606 168 Q651 128 730 186 Q817 235 844 346 Q878 466 825 533 Q790 566 734 564 Q765 543 764 515 Q766 444 714 379 Q671 301 639 224Z',92,role='hair')
add('bang-center','中央刘海','M583 174 Q615 163 634 205 C662 250 689 338 666 405 Q654 435 626 461 L610 452 L600 467 L581 462 L558 468 L575 450 Q525 413 514 354 Q503 273 535 228 Q554 191 583 174Z',93,role='hair')
add('head-bow','蓝色发侧蝴蝶结','M831 309 Q844 301 876 323 Q904 298 922 300 Q938 318 929 341 Q944 363 927 379 L903 367 L893 391 L875 374 Q849 390 839 370Z',96,role='accessory')
add('ahoge','呆毛','M421 153 C375 172 383 114 409 77 C444 35 500 9 543 10 C614 5 644 61 619 142 L599 175 L593 161 C621 111 616 67 586 46 C540 13 464 54 433 94 C409 124 398 151 421 153Z',97,role='hair')

for part in parts:
    if part['role']=='hair' and not part['name'].startswith('back-hair'):
        part['condition']='blue'

reserves={
 'back-hair-r':'<path d="M605 179 C411 162 334 286 319 428 Q353 551 260 693 Q227 849 261 983 Q416 1021 609 891Z" fill="url(#hair-fill)"/>',
 'back-hair-l':'<path d="M598 179 C786 158 875 285 884 434 Q864 563 946 681 Q1000 844 959 985 Q800 1022 598 891Z" fill="url(#hair-fill)"/>',
 'face':'<path d="M425 413 C416 302 478 218 604 216 C726 215 794 305 784 429 L777 521 Q758 602 606 617 Q454 608 427 534Z" fill="url(#face-fill)"/>',
 'topwear':'<path d="M491 630 Q599 607 698 635 Q735 703 702 790 Q602 824 485 789 Q462 708 491 630Z" fill="url(#cloth-fill)"/>',
 'skirt':'<path d="M508 795 Q600 804 690 801 C752 877 837 960 900 1035 Q847 1123 602 1153 Q380 1134 291 1040Z" fill="url(#cloth-fill)"/>',
 'eyewhite-r':'<path d="M432 474 C439 441 463 421 490 424 C533 422 548 458 539 495 Q528 526 489 521 Q443 517 432 474Z" fill="#fff9f4"/>',
 'eyewhite-l':'<path d="M652 474 C653 439 676 422 704 424 C743 423 763 447 767 473 Q762 515 715 521 Q665 522 652 474Z" fill="#fff9f4"/>',
 'apron':'<path d="M510 830 Q599 852 686 831 C697 858 716 910 716 955 Q724 1003 675 1024 Q592 1047 535 1015 Q466 991 475 939 Q487 861 510 830Z" fill="url(#apron-fill)"/>'
}
for part in parts:
    if part['name'] in reserves: part['underpaint']=reserves[part['name']]
    if part['name'] in ['hand-r','hand-l','leg-r','leg-l','neck']:
        part['condition']='skinzone'
    if part['name'] in ['head-frill','skirt-hem','cuff-r','cuff-l']:
        part['condition']='whitezone'
    if part['name'] in ['sock-bow-r','sock-bow-l']:
        part['condition']='blue'
    if part['name']=='neck':
        part['path']='M572 609 L631 610 L629 629 L603 644 L572 630Z'
    if part['name']=='mouth-open':
        part['path']='M570 536 L580 537 L596 532 L612 536 L625 536 Q634 559 615 579 Q595 591 580 579 Q567 562 570 536Z'
    if part['name']=='tail':
        part['path']='M703 1100 L901 1035 L958 986 L1026 995 L1080 870 L1220 850 L1220 1300 L750 1320Z'

defs='''<linearGradient id="skin-fill" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#ffc6b9"/><stop offset=".5" stop-color="#ffe6d7"/><stop offset="1" stop-color="#ffd6c9"/></linearGradient>
<radialGradient id="face-fill" cx=".49" cy=".66" r=".7"><stop stop-color="#ffebdd"/><stop offset=".7" stop-color="#ffe4d6"/><stop offset="1" stop-color="#ffc3b7"/></radialGradient>
<linearGradient id="hair-fill" x1="0" y1="0" x2=".1" y2="1"><stop stop-color="#334b8a"/><stop offset=".56" stop-color="#3f66aa"/><stop offset="1" stop-color="#68b7ec"/></linearGradient>
<radialGradient id="cloth-fill"><stop stop-color="#374875"/><stop offset="1" stop-color="#283357"/></radialGradient>
<linearGradient id="apron-fill" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#fff7f2"/><stop offset=".6" stop-color="#fffaf5"/><stop offset="1" stop-color="#f2e5e5"/></linearGradient>'''
(ROOT/'shared-defs.svgfrag').write_text(defs,encoding='utf-8')

(ROOT/'masks').mkdir(exist_ok=True)
(ROOT/'parts').mkdir(exist_ok=True)
(ROOT/'parts/svg').mkdir(exist_ok=True)
(ROOT/'parts/png').mkdir(exist_ok=True)
(ROOT/'work').mkdir(exist_ok=True)
(ROOT/'parts-spec.json').write_text(json.dumps({'width':w,'height':h,'parts':parts},ensure_ascii=False,indent=2),encoding='utf-8')
print('Prepared source alpha and',len(parts),'semantic regions')
