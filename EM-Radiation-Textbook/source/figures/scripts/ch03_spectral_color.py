"""Helper: approximate sRGB color of monochromatic light of a given wavelength (nm).

Method: CIE 1931 2-degree colour-matching functions (standard table, 10 nm steps, linearly
interpolated) -> linear sRGB. Spectral colors lie outside the sRGB gamut, so negative channels
are clipped, the color is normalised to full brightness, and a gentle fade is applied at the
ends of the visible range where the eye's sensitivity drops. Used by ch02_* and ch03_* scripts.
"""

# wavelength (nm): (xbar, ybar, zbar)  -- CIE 1931 2-degree standard observer
_CMF = {
    380: (0.001368, 0.000039, 0.006450), 390: (0.004243, 0.000120, 0.020050),
    400: (0.014310, 0.000396, 0.067850), 410: (0.043510, 0.001210, 0.207400),
    420: (0.134380, 0.004000, 0.645600), 430: (0.283900, 0.011600, 1.385600),
    440: (0.348280, 0.023000, 1.747060), 450: (0.336200, 0.038000, 1.772110),
    460: (0.290800, 0.060000, 1.669200), 470: (0.195360, 0.090980, 1.287640),
    480: (0.095640, 0.139020, 0.812950), 490: (0.032010, 0.208020, 0.465180),
    500: (0.004900, 0.323000, 0.272000), 510: (0.009300, 0.503000, 0.158200),
    520: (0.063270, 0.710000, 0.078250), 530: (0.165500, 0.862000, 0.042160),
    540: (0.290400, 0.954000, 0.020300), 550: (0.433450, 0.994950, 0.008750),
    560: (0.594500, 0.995000, 0.003900), 570: (0.762100, 0.952000, 0.002100),
    580: (0.916300, 0.870000, 0.001650), 590: (1.026300, 0.757000, 0.001100),
    600: (1.062200, 0.631000, 0.000800), 610: (1.002600, 0.503000, 0.000340),
    620: (0.854450, 0.381000, 0.000190), 630: (0.642400, 0.265000, 0.000050),
    640: (0.447900, 0.175000, 0.000020), 650: (0.283500, 0.107000, 0.0),
    660: (0.164900, 0.061000, 0.0), 670: (0.087400, 0.032000, 0.0),
    680: (0.046770, 0.017000, 0.0), 690: (0.022700, 0.008210, 0.0),
    700: (0.011359, 0.004102, 0.0), 710: (0.005790, 0.002091, 0.0),
    720: (0.002899, 0.001047, 0.0), 730: (0.001440, 0.000520, 0.0),
    740: (0.000690, 0.000249, 0.0), 750: (0.000332, 0.000120, 0.0),
    760: (0.000166, 0.000060, 0.0), 770: (0.000083, 0.000030, 0.0),
    780: (0.000042, 0.000015, 0.0),
}


def cie_xyz(lam):
    lam = max(380.0, min(780.0, float(lam)))
    lo = int(lam // 10 * 10)
    hi = min(lo + 10, 780)
    t = 0.0 if hi == lo else (lam - lo) / 10.0
    a, b = _CMF[lo], _CMF[hi]
    return tuple(a[i] + t * (b[i] - a[i]) for i in range(3))


def photopic_v(lam):
    """CIE 1924 photopic luminosity function V(lambda) (= ybar of CIE 1931)."""
    if lam < 380 or lam > 780:
        return 0.0
    return cie_xyz(lam)[1]


def _gamma(c):
    c = max(0.0, min(1.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def wavelength_rgb(lam, fade=True):
    """Return (r, g, b) in 0..1 for wavelength lam in nm (meaningful for ~380-780 nm)."""
    X, Y, Z = cie_xyz(lam)
    r = 3.2406 * X - 1.5372 * Y - 0.4986 * Z
    g = -0.9689 * X + 1.8758 * Y + 0.0415 * Z
    b = 0.0557 * X - 0.2040 * Y + 1.0570 * Z
    r, g, b = max(0.0, r), max(0.0, g), max(0.0, b)   # clip out-of-gamut (negative) channels
    mx = max(r, g, b)
    if mx <= 0:
        return (0.0, 0.0, 0.0)
    r, g, b = r / mx, g / mx, b / mx
    if fade:
        if lam < 420:
            f = 0.3 + 0.7 * (lam - 380) / 40
        elif lam > 660:
            f = 0.3 + 0.7 * (780 - lam) / 120
        else:
            f = 1.0
        f = max(0.3, min(1.0, f))
        r, g, b = r * f, g * f, b * f
    return (_gamma(r), _gamma(g), _gamma(b))


def wavelength_hex(lam, fade=True):
    r, g, b = wavelength_rgb(lam, fade)
    return "#{:02x}{:02x}{:02x}".format(round(r * 255), round(g * 255), round(b * 255))


if __name__ == "__main__":
    for l in (380, 400, 420, 450, 470, 490, 510, 530, 550, 570, 580, 590, 610, 630, 650, 700, 750):
        print(l, wavelength_hex(l))
