find ./Lightmaps -maxdepth 1 -type f -name "*denoised.hdr" -exec sh -c 'convert "{}" -set colorspace RGB -colorspace sRGB -depth 8 -auto-level "./Lightmaps_sdr/$(basename {} .hdr).png" ' \;
#find ./Lightmaps -maxdepth 1 -type f -name "*denoised.hdr" -exec sh -c './hdr2png -v --expo 1 --input "{}" "-o ./Lightmaps_sdr/$(basename {} .hdr).png" ' \;
#find ./Lightmaps -maxdepth 1 -type f -name "*denoised.hdr" -exec sh -c 'convert "{}" -set colorspace RGB -colorspace sRGB -treedepth 8 -colors 256 -depth 8 "./Lightmaps_sdr/$(basename {} .hdr).png" ' \;


# find ./Lightmaps_sdr -maxdepth 1 -type f -name "*.png" -exec sh -c 'cwebp -q 90 "{}" -o "./Lightmaps_sdr/$(basename {} .png).webp" ' \;
# find ./Lightmaps_sdr -maxdepth 1 -type f -name "*.png" -exec sh -c 'toktx --t2 --target_type RGB --bcmp --clevel 5 --qlevel 255 --levels 1 "./Lightmaps_sdr/$(basename {} .png)_bcmp.ktx2" "{}"' \;
find ./Lightmaps_sdr -maxdepth 1 -type f -name "*.png" -exec sh -c './toktx.exe --t2 --target_type RGB --uastc 4 --zcmp 22 --levels 1 "./Lightmaps_sdr/$(basename {} .png)_uastc.ktx2" "{}"' \;


# convert nx.hdr -set colorspace RGB -colorspace sRGB -fx "ceil(clamp(max( max( (r * (1 / 6)), (g * (1 / 6)) ), max( (b * (1 / 6)), 1e-6 ) )) * 255) / 255" - | convert -channel RGB nx.hdr - -fx "u/v" -channel A -fx 'u' nx.png
# convert nx.hdr -set colorspace RGB -colorspace sRGB -fx "ceil(clamp(max( max( (r * (1 / 6)), (g * (1 / 6)) ), max( (b * (1 / 6)), 1e-6 ) )) * 255) / 255" - | convert nx.hdr -set colorspace RGB -colorspace sRGB - -channel-fx '| gray=>alpha' nx.png
# convert nx.hdr -set colorspace RGB -colorspace sRGB -fx "ceil(clamp( max( max( r*(1.0/16.0), g*(1.0/16.0) ), max( b*(1.0/16.0), 1e-6 ) ) ) * 255.0) / 255" nx.png

