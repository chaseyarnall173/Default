"""Shared color helpers for Chapter 8/9 figure scripts.
- cie_xyz_bar(lam_nm): analytic multi-lobe Gaussian fit to the CIE 1931 2-degree
  color-matching functions (Wyman, Sloan & Shirley 2013 fit).
- spectrum_to_srgb(lam_nm, S): integrate a spectrum to XYZ, convert to gamma-encoded sRGB.
- wavelength_rgb(lam_nm): approximate display color of a single wavelength (Bruton-style)."""
import numpy as np

def _g(x, mu, s1, s2):
    s = np.where(x < mu, s1, s2)
    return np.exp(-0.5 * ((x - mu) / s) ** 2)

def cie_xyz_bar(l):
    l = np.asarray(l, float)
    x = 1.056 * _g(l, 599.8, 37.9, 31.0) + 0.362 * _g(l, 442.0, 16.0, 26.7) - 0.065 * _g(l, 501.1, 20.4, 26.2)
    y = 0.821 * _g(l, 568.8, 46.9, 40.5) + 0.286 * _g(l, 530.9, 16.3, 31.1)
    z = 1.217 * _g(l, 437.0, 11.8, 36.0) + 0.681 * _g(l, 459.0, 26.0, 13.8)
    return x, y, z

M = np.array([[3.2406, -1.5372, -0.4986], [-0.9689, 1.8758, 0.0415], [0.0557, -0.2040, 1.0570]])

def xyz_to_srgb(XYZ):
    rgb = M @ np.asarray(XYZ, float)
    if rgb.min() < 0:            # out of gamut: add white until nothing is negative
        rgb = rgb - rgb.min()
    rgb = np.clip(rgb, 0, None)
    def gam(c):
        return np.where(c <= 0.0031308, 12.92 * c, 1.055 * np.power(c, 1 / 2.4) - 0.055)
    return np.clip(gam(rgb), 0, 1)

def spectrum_to_xyz(l, S):
    x, y, z = cie_xyz_bar(l)
    return np.array([np.trapezoid(S * x, l), np.trapezoid(S * y, l), np.trapezoid(S * z, l)])

def hexcolor(rgb):
    r, g, b = (int(round(255 * c)) for c in rgb)
    return f"#{r:02x}{g:02x}{b:02x}"

def wavelength_rgb(w):
    """Approximate sRGB for a monochromatic wavelength in nm (380-750), Bruton's scheme."""
    if 380 <= w < 440: r, g, b = -(w - 440) / 60, 0.0, 1.0
    elif w < 490: r, g, b = 0.0, (w - 440) / 50, 1.0
    elif w < 510: r, g, b = 0.0, 1.0, -(w - 510) / 20
    elif w < 580: r, g, b = (w - 510) / 70, 1.0, 0.0
    elif w < 645: r, g, b = 1.0, -(w - 645) / 65, 0.0
    else: r, g, b = 1.0, 0.0, 0.0
    f = 0.3 + 0.7 * (w - 380) / 40 if w < 420 else (0.3 + 0.7 * (750 - w) / 70 if w > 680 else 1.0)
    return tuple((c * f) ** 0.8 for c in (r, g, b))
