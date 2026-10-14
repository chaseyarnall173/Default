"""Small color-science helpers shared by the Chapter 7 figure scripts.
- cmf(lam): CIE 1931 2-degree color-matching functions, multi-lobe Gaussian fit of
  Wyman, Sloan & Shirley (2013), accurate to a few percent; plenty for illustrations.
- planck(lam, T): blackbody spectrum, used as a daylight-like illuminant (T = 6500 K).
- reflectance_to_hex(R): color of a surface with reflectance R(lam) under that illuminant,
  white-balanced so a perfect white reflector maps to #ffffff.
- spectral(lam): vivid display color for a single wavelength (Bruton-style ramp)."""
import numpy as np

LAM = np.arange(380.0, 781.0, 1.0)


def _g(x, mu, s1, s2):
    s = np.where(x < mu, s1, s2)
    return np.exp(-0.5 * ((x - mu) / s) ** 2)


def cmf(lam):
    x = 1.056 * _g(lam, 599.8, 37.9, 31.0) + 0.362 * _g(lam, 442.0, 16.0, 26.7) - 0.065 * _g(lam, 501.1, 20.4, 26.2)
    y = 0.821 * _g(lam, 568.8, 46.9, 40.5) + 0.286 * _g(lam, 530.9, 16.3, 31.1)
    z = 1.217 * _g(lam, 437.0, 11.8, 36.0) + 0.681 * _g(lam, 459.0, 26.0, 13.8)
    return x, y, z


def planck(lam_nm, T=6500.0):
    lam = lam_nm * 1e-9
    h, c, k = 6.626e-34, 3.0e8, 1.381e-23
    return 1.0 / (lam ** 5 * (np.exp(h * c / (lam * k * T)) - 1.0))


M = np.array([[3.2406, -1.5372, -0.4986], [-0.9689, 1.8758, 0.0415], [0.0557, -0.2040, 1.0570]])


def _xyz(R):
    S = planck(LAM)
    x, y, z = cmf(LAM)
    return np.array([np.sum(S * R * x), np.sum(S * R * y), np.sum(S * R * z)])


_WHITE_RGB = M @ _xyz(np.ones_like(LAM))


def _gamma(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, 12.92 * c, 1.055 * c ** (1 / 2.4) - 0.055)


def linear_rgb(R):
    return (M @ _xyz(R)) / _WHITE_RGB


def to_hex(lin, exposure=1.0):
    rgb = _gamma(np.asarray(lin) * exposure)
    return "#%02x%02x%02x" % tuple(int(round(255 * v)) for v in rgb)


def reflectance_to_hex(R, exposure=1.0):
    return to_hex(linear_rgb(R), exposure)


def spectral(lam):
    if lam < 440: r, g, b = -(lam - 440) / 60, 0, 1
    elif lam < 490: r, g, b = 0, (lam - 440) / 50, 1
    elif lam < 510: r, g, b = 0, 1, -(lam - 510) / 20
    elif lam < 580: r, g, b = (lam - 510) / 70, 1, 0
    elif lam < 645: r, g, b = 1, -(lam - 645) / 65, 0
    else: r, g, b = 1, 0, 0
    f = 0.3 + 0.7 * (lam - 380) / 40 if lam < 420 else (0.3 + 0.7 * (780 - lam) / 80 if lam > 700 else 1)
    return tuple((max(0, v) * f) ** 0.8 for v in (r, g, b))


def spectral_hex(lam, dim=1.0):
    return "#%02x%02x%02x" % tuple(int(round(255 * v * dim)) for v in spectral(lam))
