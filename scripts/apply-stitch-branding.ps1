Add-Type -AssemblyName System.Drawing

$imageDir = 'D:\University-Competition\Innovation_Entrepreneurship\new_project\picture\Stitch生成稿'
$logoPath = 'D:\University-Competition\Innovation_Entrepreneurship\project\picture\icon-512.png'

if (-not (Test-Path -LiteralPath $imageDir)) {
    throw "Stitch 设计稿目录不存在：$imageDir"
}

if (-not (Test-Path -LiteralPath $logoPath)) {
    throw "原项目 Logo 不存在：$logoPath"
}

$logoSource = [System.Drawing.Bitmap]::FromFile($logoPath)
$logo = New-Object System.Drawing.Bitmap $logoSource.Width, $logoSource.Height, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)

# 用户指定的 icon-512.png 同时包含黑色外框和白色底板。
# 去除接近纯黑、纯白的背景，保留蓝金图形主体，供深色侧栏小尺寸展示。
for ($y = 0; $y -lt $logoSource.Height; $y++) {
    for ($x = 0; $x -lt $logoSource.Width; $x++) {
        $pixel = $logoSource.GetPixel($x, $y)
        $isWhiteBackground = $pixel.R -gt 246 -and $pixel.G -gt 246 -and $pixel.B -gt 246
        $isBlackBackground = $pixel.R -lt 8 -and $pixel.G -lt 8 -and $pixel.B -lt 8
        if ($isWhiteBackground -or $isBlackBackground) {
            $logo.SetPixel($x, $y, [System.Drawing.Color]::Transparent)
        }
        else {
            $logo.SetPixel($x, $y, $pixel)
        }
    }
}
$logoSource.Dispose()

Get-ChildItem -LiteralPath $imageDir -Filter '*.png' | ForEach-Object {
    $source = [System.Drawing.Bitmap]::FromFile($_.FullName)
    $canvas = New-Object System.Drawing.Bitmap $source.Width, $source.Height, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $graphics = [System.Drawing.Graphics]::FromImage($canvas)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
    $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    $graphics.DrawImage($source, 0, 0, $source.Width, $source.Height)

    # Stitch 偶尔会把局部页面导出为浅色主题。当前异常稿的亮色背景集中在
    # 内容标题/KPI 区和下方主体区；对这些区域执行蓝灰色反相映射，既把白底
    # 转为深蓝，也把原来的深色文字转为浅色，避免简单盖色导致内容消失。
    $brightPixelCount = 0
    for ($scanY = 0; $scanY -lt $source.Height; $scanY++) {
        for ($scanX = 0; $scanX -lt $source.Width; $scanX++) {
            $scanPixel = $source.GetPixel($scanX, $scanY)
            if ($scanPixel.R -ge 235 -and $scanPixel.G -ge 235 -and $scanPixel.B -ge 235) {
                $brightPixelCount++
            }
        }
    }

    $brightRatio = $brightPixelCount / ($source.Width * $source.Height)
    if ($brightRatio -gt 0.02) {
        $themeRegions = @(
            [System.Drawing.Rectangle]::new([int](93 * $source.Width / 512), [int](24 * $source.Height / 410), [int](419 * $source.Width / 512), [int](59 * $source.Height / 410)),
            [System.Drawing.Rectangle]::new([int](93 * $source.Width / 512), [int](115 * $source.Height / 410), [int](419 * $source.Width / 512), [int](295 * $source.Height / 410))
        )

        foreach ($region in $themeRegions) {
            for ($regionY = $region.Top; $regionY -lt $region.Bottom; $regionY++) {
                for ($regionX = $region.Left; $regionX -lt $region.Right; $regionX++) {
                    $pixel = $canvas.GetPixel($regionX, $regionY)
                    $maxChannel = [Math]::Max($pixel.R, [Math]::Max($pixel.G, $pixel.B))
                    $minChannel = [Math]::Min($pixel.R, [Math]::Min($pixel.G, $pixel.B))
                    $saturation = $maxChannel - $minChannel

                    if ($saturation -lt 38) {
                        $luminance = ($pixel.R + $pixel.G + $pixel.B) / 3.0
                        $inverted = [Math]::Max(18, [Math]::Min(232, 238 - (0.87 * $luminance)))
                        if ($inverted -lt 86) {
                            $newR = [int]($inverted * 0.48)
                            $newG = [int]($inverted * 0.68)
                            $newB = [int]($inverted)
                        }
                        else {
                            $newR = [int]($inverted * 0.86)
                            $newG = [int]($inverted * 0.93)
                            $newB = [int]($inverted)
                        }
                        $canvas.SetPixel($regionX, $regionY, [System.Drawing.Color]::FromArgb($pixel.A, $newR, $newG, $newB))
                    }
                }
            }
        }
    }

    # 浅色主题初次转换后，交替表格行可能留下大面积浅灰底。
    # 仅当内容区浅灰中性色仍超过 5% 时处理，保证脚本重复运行不会反复改色。
    $lightNeutralCount = 0
    for ($scanY = [int](115 * $source.Height / 410); $scanY -lt $source.Height; $scanY++) {
        for ($scanX = [int](93 * $source.Width / 512); $scanX -lt $source.Width; $scanX++) {
            $scanPixel = $canvas.GetPixel($scanX, $scanY)
            $scanMax = [Math]::Max($scanPixel.R, [Math]::Max($scanPixel.G, $scanPixel.B))
            $scanMin = [Math]::Min($scanPixel.R, [Math]::Min($scanPixel.G, $scanPixel.B))
            $scanLuminance = ($scanPixel.R + $scanPixel.G + $scanPixel.B) / 3.0
            if (($scanMax - $scanMin) -lt 42 -and $scanLuminance -gt 145) {
                $lightNeutralCount++
            }
        }
    }

    $contentPixelCount = ($source.Width - [int](93 * $source.Width / 512)) * ($source.Height - [int](115 * $source.Height / 410))
    if (($lightNeutralCount / $contentPixelCount) -gt 0.05) {
        $lightThemeBands = @(
            [System.Drawing.Rectangle]::new([int](102 * $source.Width / 512), [int](120 * $source.Height / 410), [int](293 * $source.Width / 512), [int](46 * $source.Height / 410)),
            [System.Drawing.Rectangle]::new([int](102 * $source.Width / 512), [int](166 * $source.Height / 410), [int](293 * $source.Width / 512), [int](38 * $source.Height / 410)),
            [System.Drawing.Rectangle]::new([int](102 * $source.Width / 512), [int](242 * $source.Height / 410), [int](293 * $source.Width / 512), [int](47 * $source.Height / 410)),
            [System.Drawing.Rectangle]::new([int](401 * $source.Width / 512), [int](120 * $source.Height / 410), [int](111 * $source.Width / 512), [int](290 * $source.Height / 410))
        )

        foreach ($band in $lightThemeBands) {
            $bandLuminanceTotal = 0.0
            for ($sampleY = $band.Top; $sampleY -lt $band.Bottom; $sampleY++) {
                for ($sampleX = $band.Left; $sampleX -lt $band.Right; $sampleX++) {
                    $samplePixel = $canvas.GetPixel($sampleX, $sampleY)
                    $bandLuminanceTotal += ($samplePixel.R + $samplePixel.G + $samplePixel.B) / 3.0
                }
            }
            $bandAverageLuminance = $bandLuminanceTotal / ($band.Width * $band.Height)
            if ($bandAverageLuminance -lt 105) {
                continue
            }

            for ($bandY = $band.Top; $bandY -lt $band.Bottom; $bandY++) {
                for ($bandX = $band.Left; $bandX -lt $band.Right; $bandX++) {
                    $pixel = $canvas.GetPixel($bandX, $bandY)
                    $maxChannel = [Math]::Max($pixel.R, [Math]::Max($pixel.G, $pixel.B))
                    $minChannel = [Math]::Min($pixel.R, [Math]::Min($pixel.G, $pixel.B))
                    $luminance = ($pixel.R + $pixel.G + $pixel.B) / 3.0

                    if (($maxChannel - $minChannel) -lt 48) {
                        if ($luminance -gt 135) {
                            $target = [System.Drawing.Color]::FromArgb($pixel.A, 19, 41, 68)
                        }
                        elseif ($luminance -lt 95) {
                            $target = [System.Drawing.Color]::FromArgb($pixel.A, 207, 224, 240)
                        }
                        else {
                            $target = [System.Drawing.Color]::FromArgb($pixel.A, 108, 137, 166)
                        }
                        $canvas.SetPixel($bandX, $bandY, $target)
                    }
                }
            }
        }
    }

    # 摄像头管理稿曾混入浅色主题，低分辨率反色会损伤小字号文字。
    # 对受影响最明显的 KPI、表头和详情面板进行代码化局部重绘，保持其余数据行不变。
    if ($_.Name -eq '03-摄像头管理.png') {
        $panelBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 15, 32, 53))
        $panelHighBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 19, 41, 68))
        $headerBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 11, 25, 43))
        $textBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 234, 243, 255))
        $mutedBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 145, 168, 196))
        $cyanBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 34, 211, 238))
        $dangerBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 240, 68, 82))
        $successBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 36, 200, 139))
        $panelPen = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(255, 37, 65, 95)), ([Math]::Max(1, [int]$scale))
        $cyanPen = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(255, 34, 211, 238)), ([Math]::Max(1, [int]$scale))
        $smallFont = New-Object System.Drawing.Font 'Microsoft YaHei UI', ([single](5.2 * $scale)), ([System.Drawing.FontStyle]::Regular), ([System.Drawing.GraphicsUnit]::Pixel)
        $smallBoldFont = New-Object System.Drawing.Font 'Microsoft YaHei UI', ([single](5.8 * $scale)), ([System.Drawing.FontStyle]::Bold), ([System.Drawing.GraphicsUnit]::Pixel)
        $metricFont = New-Object System.Drawing.Font 'Cascadia Code', ([single](10.5 * $scale)), ([System.Drawing.FontStyle]::Bold), ([System.Drawing.GraphicsUnit]::Pixel)

        $metricCards = @(
            @{ X = 102; Label = '摄像头总数'; Value = '156'; Suffix = '台'; Color = $cyanBrush },
            @{ X = 204; Label = '在线率'; Value = '97.4%'; Suffix = ''; Color = $successBrush },
            @{ X = 306; Label = '今日告警'; Value = '3'; Suffix = '起'; Color = $dangerBrush },
            @{ X = 408; Label = '存储状态'; Value = '100%'; Suffix = '正常'; Color = $successBrush }
        )
        foreach ($card in $metricCards) {
            $cardRect = New-Object System.Drawing.Rectangle ([int]($card.X * $scale)), ([int](35 * $scale)), ([int](94 * $scale)), ([int](43 * $scale))
            $graphics.FillRectangle($panelBrush, $cardRect)
            $graphics.DrawRectangle($panelPen, $cardRect)
            $graphics.FillRectangle($card.Color, $cardRect.X, $cardRect.Bottom - [int](2 * $scale), $cardRect.Width, [int](2 * $scale))
            $graphics.DrawString($card.Label, $smallFont, $mutedBrush, ([single](($card.X + 7) * $scale)), ([single](41 * $scale)))
            $graphics.DrawString($card.Value, $metricFont, $card.Color, ([single](($card.X + 7) * $scale)), ([single](54 * $scale)))
            if ($card.Suffix) {
                $graphics.DrawString($card.Suffix, $smallFont, $mutedBrush, ([single](($card.X + 58) * $scale)), ([single](60 * $scale)))
            }
        }

        # 重绘筛选工具栏，清除原稿中 x=93–511、y=83–114 的连续白色底板。
        $toolbarRect = New-Object System.Drawing.Rectangle ([int](93 * $scale)), ([int](83 * $scale)), ([int](419 * $scale)), ([int](32 * $scale))
        $graphics.FillRectangle($headerBrush, $toolbarRect)
        $graphics.DrawRectangle($panelPen, $toolbarRect)
        $controlRects = @(
            @{ X = 103; W = 106; Text = '搜索设备名称或编号' },
            @{ X = 214; W = 65; Text = '所有状态' },
            @{ X = 284; W = 65; Text = '所有类型' },
            @{ X = 354; W = 47; Text = '筛选' }
        )
        foreach ($control in $controlRects) {
            $controlRect = New-Object System.Drawing.Rectangle ([int]($control.X * $scale)), ([int](91 * $scale)), ([int]($control.W * $scale)), ([int](17 * $scale))
            $graphics.FillRectangle($panelBrush, $controlRect)
            $graphics.DrawRectangle($panelPen, $controlRect)
            $graphics.DrawString($control.Text, $smallFont, $mutedBrush, ([single](($control.X + 6) * $scale)), ([single](96 * $scale)))
        }
        $addRect = New-Object System.Drawing.Rectangle ([int](447 * $scale)), ([int](90 * $scale)), ([int](54 * $scale)), ([int](19 * $scale))
        $graphics.FillRectangle($cyanBrush, $addRect)
        $graphics.DrawString('+ 新增摄像头', $smallBoldFont, $headerBrush, ([single](454 * $scale)), ([single](96 * $scale)))

        $tableTitleRect = New-Object System.Drawing.Rectangle ([int](102 * $scale)), ([int](120 * $scale)), ([int](293 * $scale)), ([int](46 * $scale))
        $graphics.FillRectangle($panelBrush, $tableTitleRect)
        $graphics.DrawRectangle($panelPen, $tableTitleRect)
        $graphics.DrawString('设备列表', $smallBoldFont, $textBrush, ([single](109 * $scale)), ([single](126 * $scale)))
        $graphics.DrawString('显示 1–4 / 156 条', $smallFont, $mutedBrush, ([single](331 * $scale)), ([single](126 * $scale)))
        $graphics.FillRectangle($headerBrush, [int](103 * $scale), [int](142 * $scale), [int](291 * $scale), [int](23 * $scale))
        $columnLabels = @(
            @{ X = 110; Text = '状态' }, @{ X = 139; Text = '设备名称' }, @{ X = 203; Text = '连接状态' },
            @{ X = 252; Text = 'IP 地址' }, @{ X = 305; Text = '运行状态' }, @{ X = 370; Text = '操作' }
        )
        foreach ($column in $columnLabels) {
            $graphics.DrawString($column.Text, $smallFont, $mutedBrush, ([single]($column.X * $scale)), ([single](150 * $scale)))
        }

        # 将四行设备缩略图的浅灰底板改为深色卡片，并绘制统一线性摄像头图标。
        $thumbnailRows = @(
            @{ Y = 176; Color = $cyanBrush },
            @{ Y = 215; Color = $mutedBrush },
            @{ Y = 254; Color = $dangerBrush },
            @{ Y = 301; Color = $mutedBrush }
        )
        foreach ($thumb in $thumbnailRows) {
            $thumbRect = New-Object System.Drawing.Rectangle ([int](127 * $scale)), ([int]($thumb.Y * $scale)), ([int](27 * $scale)), ([int](18 * $scale))
            $graphics.FillRectangle($headerBrush, $thumbRect)
            $graphics.DrawRectangle($panelPen, $thumbRect)
            $iconPen = New-Object System.Drawing.Pen $thumb.Color.Color, ([Math]::Max(1, [int]$scale))
            $graphics.DrawRectangle($iconPen, [int](135 * $scale), [int](($thumb.Y + 5) * $scale), [int](10 * $scale), [int](7 * $scale))
            $graphics.DrawEllipse($iconPen, [int](138 * $scale), [int](($thumb.Y + 7) * $scale), [int](3 * $scale), [int](3 * $scale))
            $graphics.DrawLine($iconPen, [int](145 * $scale), [int](($thumb.Y + 7) * $scale), [int](149 * $scale), [int](($thumb.Y + 5) * $scale))
            $graphics.DrawLine($iconPen, [int](149 * $scale), [int](($thumb.Y + 5) * $scale), [int](149 * $scale), [int](($thumb.Y + 12) * $scale))
            $graphics.DrawLine($iconPen, [int](149 * $scale), [int](($thumb.Y + 12) * $scale), [int](145 * $scale), [int](($thumb.Y + 10) * $scale))
            $iconPen.Dispose()
        }

        $detailRect = New-Object System.Drawing.Rectangle ([int](401 * $scale)), ([int](120 * $scale)), ([int](111 * $scale)), ([int](290 * $scale))
        $graphics.FillRectangle($panelBrush, $detailRect)
        $graphics.DrawRectangle($panelPen, $detailRect)
        $graphics.FillRectangle($headerBrush, $detailRect.X + 1, $detailRect.Y + 1, $detailRect.Width - 2, [int](27 * $scale))
        $graphics.DrawString('设备详情与状态', $smallBoldFont, $textBrush, ([single](408 * $scale)), ([single](128 * $scale)))
        $graphics.FillRectangle($cyanBrush, [int](405 * $scale), [int](154 * $scale), [int](2 * $scale), [int](50 * $scale))
        $detailRows = @(
            @{ Y = 154; Label = '设备名称'; Value = '擎安智吊摄像机-01' },
            @{ Y = 170; Label = '设备编号'; Value = 'CAM-HJ-0921' },
            @{ Y = 186; Label = 'IP 地址'; Value = '192.168.18.101' },
            @{ Y = 202; Label = '运行状态'; Value = '在线 · 正常' }
        )
        foreach ($row in $detailRows) {
            $graphics.DrawString($row.Label, $smallFont, $mutedBrush, ([single](411 * $scale)), ([single]($row.Y * $scale)))
            $graphics.DrawString($row.Value, $smallBoldFont, $textBrush, ([single](444 * $scale)), ([single]($row.Y * $scale)))
        }
        $graphics.DrawLine($panelPen, [int](408 * $scale), [int](224 * $scale), [int](504 * $scale), [int](224 * $scale))
        $graphics.DrawString('最近告警', $smallBoldFont, $textBrush, ([single](408 * $scale)), ([single](234 * $scale)))
        $graphics.DrawString('●  周界入侵告警', $smallFont, $dangerBrush, ([single](410 * $scale)), ([single](252 * $scale)))
        $graphics.DrawString('2026-07-21 10:30:12', $smallFont, $mutedBrush, ([single](416 * $scale)), ([single](264 * $scale)))
        $graphics.DrawString('●  视频信号恢复', $smallFont, $successBrush, ([single](410 * $scale)), ([single](286 * $scale)))
        $graphics.DrawString('2026-07-21 09:42:15', $smallFont, $mutedBrush, ([single](416 * $scale)), ([single](298 * $scale)))
        $graphics.FillRectangle($panelHighBrush, [int](408 * $scale), [int](374 * $scale), [int](45 * $scale), [int](25 * $scale))
        $graphics.FillRectangle($panelHighBrush, [int](458 * $scale), [int](374 * $scale), [int](46 * $scale), [int](25 * $scale))
        $graphics.DrawRectangle($panelPen, [int](408 * $scale), [int](374 * $scale), [int](45 * $scale), [int](25 * $scale))
        $graphics.DrawRectangle($cyanPen, [int](458 * $scale), [int](374 * $scale), [int](46 * $scale), [int](25 * $scale))
        $graphics.DrawString('重启设备', $smallBoldFont, $textBrush, ([single](418 * $scale)), ([single](383 * $scale)))
        $graphics.DrawString('配置参数', $smallBoldFont, $cyanBrush, ([single](468 * $scale)), ([single](383 * $scale)))

        $panelBrush.Dispose(); $panelHighBrush.Dispose(); $headerBrush.Dispose(); $textBrush.Dispose(); $mutedBrush.Dispose()
        $cyanBrush.Dispose(); $dangerBrush.Dispose(); $successBrush.Dispose(); $panelPen.Dispose(); $cyanPen.Dispose()
        $smallFont.Dispose(); $smallBoldFont.Dispose(); $metricFont.Dispose()
    }

    # Stitch 导出稿当前为 512x410；按画布宽度缩放坐标，兼容后续高清导出。
    $scale = $source.Width / 512.0
    $sidebarWidth = [int][Math]::Round(92 * $scale)
    $brandHeight = [int][Math]::Round(31 * $scale)
    $footerTop = [int][Math]::Round(384 * $scale)
    $footerHeight = $source.Height - $footerTop

    $sidebarBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 8, 20, 38))
    $borderPen = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(255, 37, 65, 95)), ([Math]::Max(1, [int][Math]::Round($scale)))

    # 重建左上品牌区：使用原项目蓝金 Logo 与“擎安智吊”。
    $graphics.FillRectangle($sidebarBrush, 0, 0, $sidebarWidth, $brandHeight)
    $graphics.DrawLine($borderPen, 0, $brandHeight - 1, $sidebarWidth, $brandHeight - 1)
    $logoX = [int][Math]::Round(5 * $scale)
    $logoY = [int][Math]::Round(5 * $scale)
    $logoW = [int][Math]::Round(16 * $scale)
    $logoH = [int][Math]::Round(20 * $scale)
    $graphics.DrawImage($logo, $logoX, $logoY, $logoW, $logoH)

    $titleFont = New-Object System.Drawing.Font 'Microsoft YaHei UI', ([single](8.2 * $scale)), ([System.Drawing.FontStyle]::Bold), ([System.Drawing.GraphicsUnit]::Pixel)
    $subFont = New-Object System.Drawing.Font 'Microsoft YaHei UI', ([single](4.4 * $scale)), ([System.Drawing.FontStyle]::Regular), ([System.Drawing.GraphicsUnit]::Pixel)
    $titleBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 234, 243, 255))
    $subBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 112, 143, 176))
    $graphics.DrawString('擎安智吊', $titleFont, $titleBrush, ([single](25 * $scale)), ([single](6 * $scale)))
    $graphics.DrawString('吊装安全运营平台', $subFont, $subBrush, ([single](25 * $scale)), ([single](17 * $scale)))

    # 将左下角英文用户信息统一替换为中文。
    if ($footerHeight -gt 0) {
        $textLeft = [int][Math]::Round(25 * $scale)
        $graphics.FillRectangle($sidebarBrush, $textLeft, $footerTop, $sidebarWidth - $textLeft, $footerHeight)
        $userFont = New-Object System.Drawing.Font 'Microsoft YaHei UI', ([single](6.2 * $scale)), ([System.Drawing.FontStyle]::Bold), ([System.Drawing.GraphicsUnit]::Pixel)
        $roleFont = New-Object System.Drawing.Font 'Microsoft YaHei UI', ([single](4.5 * $scale)), ([System.Drawing.FontStyle]::Regular), ([System.Drawing.GraphicsUnit]::Pixel)
        $graphics.DrawString('安全管理员', $userFont, $titleBrush, ([single](27 * $scale)), ([single](388 * $scale)))
        $graphics.DrawString('系统管理员', $roleFont, $subBrush, ([single](27 * $scale)), ([single](397 * $scale)))
        $userFont.Dispose()
        $roleFont.Dispose()
    }

    $graphics.Dispose()
    $source.Dispose()
    $sidebarBrush.Dispose()
    $borderPen.Dispose()
    $titleFont.Dispose()
    $subFont.Dispose()
    $titleBrush.Dispose()
    $subBrush.Dispose()

    $tempPath = $_.FullName + '.branding.png'
    $canvas.Save($tempPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $canvas.Dispose()
    Move-Item -LiteralPath $tempPath -Destination $_.FullName -Force
}

$logo.Dispose()



