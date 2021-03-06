library thIdent;

{ Important note about DLL memory management: ShareMem must be the
  first unit in your library's USES clause AND your project's (select
  Project-View Source) USES clause if your DLL exports any procedures or
  functions that pass strings as parameters or function results. This
  applies to all strings passed to and from your DLL--even those that
  are nested in records and classes. ShareMem is the interface unit to
  the BORLNDMM.DLL shared memory manager, which must be deployed along
  with your DLL. To avoid using BORLNDMM.DLL, pass string information
  using PChar or ShortString parameters. }

uses
  SysUtils,
  Classes;

{$R *.res}

type TResType = array[1..6] of real;

(*
1 -  Sand
2 -  Loamy sand
3 -  Sandy loam
4 -  Loam
5 -  Silt
6 -  Silt loam
7 -  Sandy clay loam
8 -  Clay loam
9 -  Silty clay loam
10 - Sandy clay
11 - Silty clay
12 - Clay
*)

function table6(cType:integer) : TResType;
var r : TResType;
begin
  r[5] := -1.0;
  r[6] := -1.0;
     case cType of
  11: begin  r[1]:=1.019; r[3]:=1.825; r[2]:=0.355; r[4]:=0.300; end;
  9: begin  r[1]:=1.762; r[3]:=1.595; r[2]:=0.339; r[4]:=0.312; end;
  6: begin  r[1]:=2.303; r[3]:=1.994; r[2]:=0.350; r[4]:=0.542; end;
  8: begin  r[1]:=1.346; r[3]:=2.883; r[2]:=0.419; r[4]:=0.302; end;
  4: begin  r[1]:=1.998; r[3]:=2.003; r[2]:=0.360; r[4]:=0.358; end;
  7: begin  r[1]:=1.838; r[3]:=2.668; r[2]:=0.314; r[4]:=0.162; end;
  3: begin  r[1]:=3.544; r[3]:=2.473; r[2]:=0.224; r[4]:=0.358; end;
  2: begin  r[1]:=3.199; r[3]:=3.852; r[2]:=0.160; r[4]:=0.627; end;
  1: begin  r[1]:=2.495; r[3]:=5.306; r[2]:=0.216; r[4]:=1.195; end;
 10: begin  r[1]:=1.280; r[3]:=3.016; r[2]:=0.289; r[4]:=0.364; end;
 12: begin  r[1]:=0.427; r[3]:=1.915; r[2]:=0.351; r[4]:=0.114; end;
  5: begin  r[1]:=2.860; r[3]:=2.317; r[2]:=0.392; r[4]:=0.615; end;
            end;
  result := r;
end;

function table13(sand, silt, clay, cc : real) : TResType;
var r : TResType;
begin
  r[5] := -1.0;
  r[6] := -1.0;
  if (sand <15)
  then
  begin
    r[1]:= -0.027475+0.073868*sand-0.160208*cc+0.028535*silt;
    r[3]:= 3.177718-0.166438*cc+0.062028*sand-0.015554*silt;
    r[2]:= 0.081161+0.005042*silt-902600*1e-7*r[1]+467560*1e-7*r[3]+0.004928*sand;
    r[4]:= 0.062381+0.035256*sand+0.048389*cc;
  end;
  if ((sand>=15) and (sand<65))
  then
  begin
    r[1]:= 3.888488-0.067144*clay-0.245297*cc;
    r[3]:= 4.072918-0.486439*cc-0.034405*clay;
    r[2]:= 0.46794-500950*1e-7*r[1];
    r[4]:= -0.958759+0.094356*cc+2780710*1e-7*r[1]+1.438943*r[2]+0.012195*clay-622380*1e-7*r[3];
  end;
  if (sand>=65)
  then
  begin
    r[1]:= 15.10342-0.13037*sand-0.7504*cc-0.04103*silt;
    r[3]:= 5.70508-1.64478*cc;
    r[2]:= 0.258403+0.026259*cc-0.003253*silt-129290*1e-7*r[3];
    r[4]:= -4.60883+0.05861*sand+0.03842*silt;
  end;
  result := r;
end;

function table10(cType : integer; sand, silt, clay : real) : TResType;
var r : TResType;
begin
  r[5] := -1.0;
  r[6] := -1.0;
  case cType of
  11: begin
       r[3]:= -1.31183 + 0.07295*clay - 0.15008*sand; {a}
       r[1]:= 1.464826 - 2446390*1E-7*r[3]; {k0}
       r[2]:= 0.312884 - 0.007097*sand - 535120*1E-7*r[1] + 0.002017*silt; {q0}
       r[4]:= 0.684129 - 2033140*1E-7*r[3];    {b}
     end;
  9: begin
       r[1]:= 7.034854 - 0.162846*clay;
       r[3]:= 1.281122 + 0.107371*sand;
       r[2]:= 0.036979 - 710500* 1E-7*r[1] + 574040* 1E-7*r[3] + 0.00516*silt;
       r[4]:= 0.519866 - 1543020* 1E-7*r[3] +1091140*1E-7*r[1];
     end;
  6: begin
       r[1]:= 1.636154 + 0.034899*clay;
       r[3]:= -0.422972 + 0.138473*clay + 0.008047*sand;
       r[2]:= 0.602315 - 1280750*1E-7*r[1] - 0.002541*sand + 0.005637*clay;
       r[4]:= 0.319662 + 0.012685*sand + 0.723989*r[2] - 942660*1E-7*r[3];
    end;
  4: begin
       r[1]:= 2.700693 - 0.036448*clay;
       r[3]:= 0.975929 + 0.034267*silt;
       r[2]:= 0.789711 - 0.007582*sand - 362850*1E-7*r[1];
       r[4]:= -1.6877 + 0.00964*clay + 1333700*1E-7*r[1] - 1679300*1E-7*r[3] + 2.0275*r[2] + 0.01537*sand;
     end;
  5,10,12 : begin     // M1
               r[1]:= 3.030598 - 0.042688*clay;
               r[3]:= 1.216889 + 0.026983*sand + 3092420*1E-7*r[1];
               r[2]:= 0.360551 + 0.000423*sand - 205470*1E-7*r[3] - 359720*1E-7*r[1] + 0.002032*silt;
               r[4]:= 0.791597 - 0.012801*clay + 777600*1E-7*r[3] - 1069080*1E-7*r[1];
  end;
  1,2,3,7,8: begin   end;
  end;
  result := r;
end;

function table11(cType : integer; sand, silt, clay, bd : real) : TResType;
var r : TResType;
begin
  r[5] := -1.0;
  r[6] := -1.0;
  case cType of
  11: begin
       r[3]:= -1.14049 + 0.00260107*bd;
       r[1]:= 0.266245 - 7860030*1E-7*r[3] + 0.001912604*bd;
       r[2]:= 0.312884 - 0.007097*sand - 535120*1E-7*r[1] + 0.002017*silt;
       r[4]:= 0.888667 - 0.00063389*bd  + 1467820*1E-7*r[1];
     end;
  9: begin
       r[1]:= -4.74319 + 0.00222585*bd + 0.06148*silt;
       r[3]:= 2.598825 + 0.001827506*bd - 0.046176*silt;
       r[2]:= 0.006559 - 1085200*1E-7*r[1] + 0.000189384*bd + 0.004822*silt;
       r[4]:= 0.519866 - 1543020*1E-7*r[3] + 1091140*1E-7*r[1];
     end;
  6: begin
       r[1]:= 1.075821 + 0.000900169*bd;
       r[3]:= -1.5424 + 0.08548*clay + 0.00120075*bd + 0.00864*sand;
       r[2]:= 0.602315 - 1280750*1E-7*r[1] - 0.002541*sand + 0.005637*clay;
       r[4]:= 1.994242 - 0.000615838*bd - 0.012363*silt + 0.59337*r[2];
     end;
  4: begin
       r[1]:= 2.700693 - 0.036448*clay;
       r[3]:= -1.4418 + 0.03191*silt + 0.0017206*bd;
       r[2]:= 0.409726 - 0.006416*sand - 390660*1E-7*r[1] + 0.000229971*bd;
       r[4]:= -1.16877 + 0.00964*clay + 1333700*1E-7*r[1] + 1679300*1E-7*r[3] + 2.0275*r[2] + 0.01537*sand;
   end;
  5,10,12 : begin     // M2
               r[1]:= 0.147405 - 0.034914*clay + 0.0016859*bd + 0.007866*silt;
               r[3]:= 0.135212 + 0.024498*sand + 0.001033355*bd + 1726810*1E-7*r[1];
               r[2]:= 0.138479 + 0.000894*sand - 255500*1E-7*r[3] - 632370*1E-7*r[1] + 0.000166817*bd + 0.003005*silt;
               r[4]:= 1.172862 - 0.010829*clay + 1063690*1E-7*r[3] - 0.000518045*bd;
  end;
  1,2,3,7,8: begin   end;
  end;
  result := r;
end;

function table12(cType : integer; sand, silt, clay, cc : real) : TResType;
var r : TResType;
begin
  r[5] := -1.0;
  r[6] := -1.0;
  case cType of
  11: begin
       r[3]:= -1.31183 + 0.07295*clay - 0.15008*sand;
       r[1]:= 4.415549 - 3569660*1E-7*r[3] - 0.154774*cc - 0.047451*clay;
       r[2]:= 0.390834 + 0.005329*cc - 410060*1E-7*r[1] - 0.00988*sand;
       r[4]:= 0.684129 - 2033140*1E-7*r[3];
     end;
  9: begin
       r[1]:= 6.605988 - 0.110533*clay - 0.214914*cc - 0.085733*sand;
       r[3]:= 1.580328 - 0.249593*cc + 0.038722*clay;
       r[2]:= 0.036979 - 710500*1E-7*r[1] + 574040*1E-7*r[3] + 0.00516*silt;
       r[4]:= 1.625873 - 4246150*1E-7*r[3] - 0.094641*cc - 0.009299*sand;
     end;
  6: begin
       r[1]:= 2.650567 - 0.157752*cc;
       r[3]:= -0.422972 + 0.138473*clay + 0.008047*sand;
       r[2]:= 0.602315 - 1280750*1E-7*r[1] - 0.002541*sand + 0.005637*clay;
       r[4]:= -0.808348 + 0.178279*cc + 0.029822*clay + 0.005526*sand + 1357460*1E-7*r[1];
     end;
  4: begin
       r[1]:= 4.04656 - 0.07951*clay - 1.04608*cc + 0.03518*silt;
       r[3]:= 0.975929 + 0.034267*silt;
       r[2]:= 1.410928 - 0.010671*sand - 1007880*1E-7*r[1] - 0.103855*cc - 0.009219*clay;
       r[4]:= -0.101648 - 0.177998*cc + 1.087707*r[2] + 0.008017*sand;
     end;
  5,10,12 : begin     // M3
              r[1]:= 2.99942 - 0.038107*clay - 0.184094*cc + 0.00667*silt;
              r[3]:= 2.442162 + 0.024185*sand - 0.247381*cc;
              r[2]:= 0.360551 + 0.000423*sand - 205470*1E-7*r[3] - 359720*1E-7*r[1] + 0.002032*silt;
              r[4]:= 0.540457 - 0.012034*clay + 1037780*1E-7*r[3] + 0.043562*cc - 703460*1E-7*r[1];
  end;
  1,2,3,7,8: begin   end;
  end;
  result := r;
end;

function u_model(sand,silt,clay:real; bd,cc:real; mode : integer) : TResType;
var r : TResType;
begin
  r[5] := -1.0;
  r[6] := -1.0;
  case mode of
  1: // SSC
  begin
     r[1]:= 3.030598 - 0.042688*clay;
     r[3]:= 1.216889 + 0.026983*sand + 3092420*1E-7*r[1];
     r[2]:= 0.360551 + 0.000423*sand - 205470*1E-7*r[3] - 359720*1E-7*r[1] + 0.002032*silt;
     r[4]:= 0.791597 - 0.012801*clay + 777600*1E-7*r[3] - 1069080*1E-7*r[1];
  end;
  2: // SSC + BD
  begin
        r[1]:= 0.147405 - 0.034914*clay + 0.0016859*bd + 0.007866*silt;
        r[3]:= 0.135212 + 0.024498*sand + 0.001033355*bd + 1726810*1E-7*r[1];
        r[2]:= 0.138479 + 0.000894*sand - 255500*1E-7*r[3] - 632370*1E-7*r[1] + 0.000166817*bd + 0.003005*silt;
        r[4]:= 1.172862 - 0.010829*clay + 1063690*1E-7*r[3] - 0.000518045*bd;
  end;
  3: // SSC + CC
  begin
    r[1]:= 2.99942 - 0.038107*clay - 0.184094*cc + 0.00667*silt;
    r[3]:= 2.442162 + 0.024185*sand - 0.247381*cc;
    r[2]:= 0.360551 + 0.000423*sand - 205470*1E-7*r[3] - 359720*1E-7*r[1] + 0.002032*silt;
    r[4]:= 0.540457 - 0.012034*clay + 1037780*1E-7*r[3] + 0.043562*cc - 703460*1E-7*r[1];
  end;
  end; {case}
  result := r;
end;

function table2a(mode : integer; tt : integer) : real;
var res : real;
begin
   res:=1300;
   if (mode=2) then res := 1.8;
   case tt of
   1: begin  if mode=1 then res:=1560 else res:=0.36; end;
   2: begin  if mode=1 then res:=1540 else res:=0.31; end;
   3: begin  if mode=1 then res:=1500 else res:=0.36; end;
   4: begin  if mode=1 then res:=1450 else res:=0.26; end;
   5: begin  if mode=1 then res:=1200 else res:=0.29; end;
   6: begin  if mode=1 then res:=1200 else res:=0.29; end;
   7: begin  if mode=1 then res:=1630 else res:=0.10; end;
   8: begin  if mode=1 then res:=1450 else res:=0.05; end;
   9: begin  if mode=1 then res:=1400 else res:=0.07; end;
  10: begin  if mode=1 then res:=1560 else res:=0.19; end;
  11: begin  if mode=1 then res:=1410 else res:=0.12; end;
  12: begin  if mode=1 then res:=1320 else res:=0.19; end;
   end {case};
   result := res;
end;

function isProper(res : TResType) : boolean;
begin
  // TODO: ���� �������������� �������� �� �������������
  isProper := (res[1]>0) and (res[2]>0) and (res[3]>0) and (res[4]>0.1);
end;

function identify(textType:integer; sand,silt,clay:real; bd,cc:real; var res : TResType) : boolean; stdcall;
var rs : TResType;
    j : integer;
    rslt : boolean;
    isSGroup : boolean;
    hc,cms,snd : real;
begin
   // ��� ��������
   rs[1] := -1.0;
   rs[2] := -1.0;
   rs[3] := -1.0;
   rs[4] := -1.0;
   rs[5] := -1.0;
   rs[6] := -1.0;
   snd := 30;
   rslt := false;
   if ((sand<0) or (silt<0) or (clay<0))
   then
   begin
      rs := table6(textType);
      case textType of
      1: snd := 90;
      2: snd := 82;
      3: snd := 63;
      4: snd := 41;
      5: snd := 8;
      6: snd := 20;
      7: snd := 60;
      8: snd := 33;
      9: snd := 10;
     10: snd := 52;
     11: snd := 8;
     12: snd := 25;
        end; {case}
      rslt := true;
   end
   else
   begin
      // ����������� ���������� ������������� �� ssc
      if ((sand>=0) and (silt>=0) and (clay>=0))
      then
      begin
        snd := sand;
        isSGroup := (textType=7) or (textType=8) or (textType<4);
        if (isSGroup)
        then
        begin
          if (cc>0)
          then
          begin
             rs := table13(sand, silt, clay, cc);
             if (not isProper(rs))
             then
               rs := u_model(sand,silt,clay,bd,cc,3);
             if ((not isProper(rs)) and (bd>0))
             then
               rs := u_model(sand,silt,clay,bd,cc,2);
             if (not isProper(rs))
             then
               rs := u_model(sand,silt,clay,bd,cc,1);
             if (not isProper(rs))
             then
               rs := table6(textType);
          end
          else
             rs := table6(textType);
        end
        else
        begin
          if (cc>0)
          then
          begin
              rs := table12(textType, sand, silt, clay, cc);
              if (not isProper(rs))
              then
                rs := u_model(sand,silt,clay,bd,cc,3);
              if ((not isProper(rs)) and (bd>0))
              then
                rs := u_model(sand,silt,clay,bd,cc,2);
              if (not isProper(rs))
              then
                rs := u_model(sand,silt,clay,bd,cc,1);
              if (not isProper(rs))
              then
                rs := table6(textType);
          end
          else
          begin
             if (bd>0)
             then
             begin
                rs := table11(textType, sand, silt, clay, bd);
                if (not isProper(rs))
                then
                   rs := u_model(sand,silt,clay,bd,cc,2);
                if (not isProper(rs))
                then
                   rs := u_model(sand,silt,clay,bd,cc,1);
                if (not isProper(rs))
                then
                  rs := table6(textType);
             end
             else
             begin
                rs := table10(textType, sand, silt, clay);
                if (not isProper(rs))
                then
                   rs := u_model(sand,silt,clay,bd,cc,1);
                if (not isProper(rs))
                then
                  rs := table6(textType);
             end;
          end;
        end;
        rslt := true;
      end
   end;

   if (rslt)
   then
   begin
     if (bd<0)
     then
     begin
        if (cc>=0)
        then
           bd:=1556*exp(-0.0*cc)
        else
          if (clay>=0)
          then
             bd := 1522.4-5*Clay
          else
             bd := table2a(1, textType);
     end;
     if (cc<0)
     then
        cc:=table2a(2, textType);


     hc := cc*0.0197;
     cms:=1924.64*hc+746.1453*(1-hc);
     rs[5]:=cms*bd;
     rs[6]:=4175470.6;
   end;

   for j:=1 to 6 do
      res[j] := rs[j];
   result := rslt;
end;

function calculateK(w:real; k0,w0,a,b: real): real; stdcall;
begin
  result := k0 + a*exp(-0.5*sqr(ln(w/w0)/b));
end;

function calculateC(w:real; C1, C2: real): real; stdcall;
begin
  result := c1+c2*w;
end;


exports
  identify,
  calculateK,
  calculateC;

begin
end.






