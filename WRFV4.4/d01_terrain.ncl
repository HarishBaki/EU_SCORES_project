
;   Example script - plot terrain (using some basic WRF scripts)
;   Overwrite basic map background settings
;   November 2008

load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/wrf/WRFUserARW.ncl"

begin

  a = addfile("geo_em.d01.nc","r")           ; Open a file


; type = "x11"
; type = "pdf"
; type = "eps"
; type = "ncgm"
  wks = gsn_open_wks("png","d01_terrain")         ; Create a plot workstation
 gsn_define_colormap(wks,"MPL_gist_earth")
; gsn_define_colormap(wks,"OceanLakeLandSnow")

  opts = True                                  ; Set some Basic Plot options
  opts@MainTitle = ""
  opts@InitTime = False                        ; Do not plot time or footers
  opts@Footer = False    

  ter = wrf_user_getvar(a,"HGT_M",0)           ; Read the variable to memory

  res = opts                                   ; Use basic options for this field
  res@cnFillOn = True                          ; Create a color fill plot
  ;res@ContourParameters = (/ 0, 430., 10. /) ; Set the levels
  res@cnLevelSelectionMode     = "ExplicitLevels"
  res@cnLevels                 = (/-1,0,0.5,1,10,50,80,120,160,200,240/)
  res@cnFillPalette        = "WhiteBlueGreenYellowRed" ; set color map

  contour = wrf_contour(a,wks,ter,res)

  pltres = True                                ; Set plot options
  mpres = True                                 ; Set map options
  mpres@mpGeophysicalLineColor      = "black"  ; Overwrite basic map settings
  mpres@mpGridLineColor             = "black"
  mpres@mpLimbLineColor             = "black"
  mpres@mpNationalLineColor         = "black"
  mpres@mpPerimLineColor            = "black"
  mpres@mpUSStateLineColor          = "black"
  mpres@mpOutlineBoundarySets = "National"
  mpres@mpGeophysicalLineThicknessF = 2
  mpres@mpNationalLineThicknessF    = 2

  
  txres        = True                                    ; text mods desired
  txres@txFont = "helvetica"
  txres@txJust = "TopCenter"
  txres@txPerimOn = False
  txres@txFontHeightF = 0.01
  txres@txFontColor= "brown"

  polyres1                          = True
  polyres1@gsMarkerIndex            = 16              ; polymarker style
  polyres1@gsMarkerSizeF            = 8.              ; polymarker size
  polyres1@gsMarkerColor            = "brown"         ; polymarker color

  polyres2                          = True
  polyres2@gsMarkerIndex            = 12              ; polymarker style
  polyres2@gsMarkerSizeF            = 8.              ; polymarker size
  polyres2@gsMarkerColor            = "brown"         ; polymarker color

  pltres@PanelPlot                  = True            ; Needed to overlay the polymarkers

  X_LAT = 52.5
  X_LON = 3

  plot = wrf_map_overlays(a,wks,(/contour/),pltres,mpres) ; Plot field over map background

  text = gsn_add_text(wks,plot,"WT1",X_LON,X_LAT-0.05,txres)
  dum1 = gsn_add_polymarker(wks,plot,X_LON,X_LAT,polyres2)

  draw(plot)
  frame(wks)

end
