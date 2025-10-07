ShellBatterySize="D-BIG"; //Battery Shell Size
StoredBatterySize="CR2450"; //Battery to be Stored
FontSize=4;  //Varies between 4-9 depending on the length of battery name and diameter of the shell.

BatteryDetails=[

    //Name      Diam    Length
    ["AAA",     10.5,   45],
    ["AA",      14,     51],
    ["C",       25.2,   47.6],
    ["D",       33,     60.6],
    ["D-BIG",   33,     62.4], // Lengthened 1.8 to accomadate the 2450 bump
    ["N",       11.5,   29],
    ["377",     6.8,    2.6],
    ["CR1225",  12.5,   2.5],
    ["CR1616",  16,     1.6],
    ["CR1620",  16,     2],
    ["CR1632",  16,     3.2],
    ["CR2016",  20,     1.6],
    ["CR2025",  20,     2.5],
    ["CR2032",  20,     3.2],
    ["CR2450",  24,     5.2], // Lengthened 0.2 to prevent sticking
    ["B357",    11.6,   5.4],
    ["LR41",    7.85,   3.5],
    ["LR44",    11.5,   5.3],
    ["CUSTOM",  5,      2]

];


//Pull values from list given search string
ShellBatterySizeDiameter=BatteryDetails[search([ShellBatterySize],BatteryDetails,1,0,num_returns_per_match=1)[0]][1];
ShellBatterySizeLength=BatteryDetails[search([ShellBatterySize],BatteryDetails,1,0,num_returns_per_match=1)[0]][2];
StoredBatterySizeDiameter=BatteryDetails[search([StoredBatterySize],BatteryDetails,1,0,num_returns_per_match=1)[0]][1];
StoredBatterySizeLength=BatteryDetails[search([StoredBatterySize],BatteryDetails,1,0,num_returns_per_match=1)[0]][2];

//Put it in the log for troubleshooting
echo(str("ShellBatterySize : ",ShellBatterySize));
echo(str("ShellBatterySizeDiameter : ",ShellBatterySizeDiameter));
echo(str("ShellBatterySizeLength : ",ShellBatterySizeLength));

echo(str("StoredBatterySize : ",StoredBatterySize));
echo(str("StoredBatterySizeDiameter : ",StoredBatterySizeDiameter));
echo(str("StoredBatterySizeLength : ",StoredBatterySizeLength));

//Set variables for module 
ShellDiameter=ShellBatterySizeDiameter;
ShellLength=ShellBatterySizeLength;


wall=1; //wall thickness
clearance=.5; //gap around cells
TotalThickness = StoredBatterySizeDiameter+(wall*2)+(clearance*2);
echo(str("TotalThickness : ",TotalThickness));  //Used to calculate minimum shell diameter to contain battery

//Run quick quick to make sure batteries will fit given buffers
if (TotalThickness<= ShellBatterySizeDiameter){

    //Make it so!
    tray(StoredBatterySizeDiameter,StoredBatterySizeLength);
}
else{

    //I cannot give it any more captain
    rotate([0,0,180])
    text("Battery too large for shell");
    
}

//Core Module

 module tray(d,h){
  bottom=-d/2-wall;
  top=d/4;
  hInc=h+wall+clearance;
  wInc=d+wall+clearance;
  nZ=floor((ShellLength-wall*2)/hInc);
  nY=floor((ShellDiameter-wall*2)/wInc);
  zMax=wall*2+(hInc*nZ);
  FontThickness=0.8;
  FontStyle="Arial:style=Narrow Bold";
  FontSpacing=1.1;
  
  rotate([0,-90,0])
  translate([0,0,0])
  
  //Combine shape and text
  union(){
  
  //Create shell with cutouts    
  difference()
  {
    //Shell Battery Main Cylinder (to be subtracted from)
    color("green") cylinder(h=ShellLength,d=ShellDiameter,$fn=100);
      
    //Cutaway - Foot of tray (for printability without supports)
    translate([(-ShellDiameter/2)+ShellDiameter/16,0,ShellLength/2])
    color("red") cube([ShellDiameter/8,ShellDiameter,ShellLength],center=true);
      
    //Cutaway - Top of tray
    translate([ShellDiameter+top,0,ShellLength/2])
    color("blue") cube([ShellDiameter*2,ShellDiameter+wall*2,ShellLength-(wall*2)],center=true);
      
    //Cutaway - Slots
    for(iZ=[0:nZ-1])
    {
      for(iY=[0:nY-1])
      {
        translate([0,iY*wInc-(nY-1)*wInc/2,iZ*hInc])
        union()
        {
          translate([0,0,(h+clearance)/2+wall*2])
          color("purple") cylinder(d=d+clearance,h=h+clearance,center=true,$fn=100);
          translate([0,-(d+clearance)/2,wall*2])
          color("orange") cube([d/2,d+clearance,h+clearance]);
        }
      }
    }

  };
  
  //Battery Name Text
  rotate([0,0,270])
  mirror([1,0,0])
  translate([0,0,-FontThickness])
  linear_extrude(FontThickness)
    text(text=StoredBatterySize, valign ="center", halign ="center", size=FontSize, font=FontStyle, spacing=FontSpacing, $fn=50);
  
  }
}
