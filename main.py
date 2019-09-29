#!/usr/bin/python3

import json
from ftplib import FTP
import gzip
import os

testStars = [30438, 21421, 91262, 3829]
testStarNames = ["Canopus", "Aldebaran", "Vega", "Van Maanen 2 in Pisces"]

def favicon(environ):
    """Return favicon."""
    status = "200 OK"
    responseHeaders = [("Content-type", "image/x-icon")]
    with open("favicon.ico", "rb") as f:
        output = f.read()
    return status, responseHeaders, output

def robots(environ):
    """Returns robots.txt"""
    status = "200 OK"
    responseHeaders = [("Content-type", "text/plain")]
    with open("robots.txt", "r") as f:
        output = f.read()
    return status, responseHeaders, output

def update(environ):
    """Updates database."""
    ftp = FTP("cdsarc.u-strasbg.fr")
    ftp.login()
    ftp.cwd("/pub/cats/I/239")
    with open("hip_main.dat.gz", "wb") as f:
        ftp.retrbinary("RETR hip_main.dat.gz", f.write)
    ftp.quit()
    print("/update: File Downloaded.")
    with gzip.open("hip_main.dat.gz", "rb") as f:
        text = f.read()
    os.remove("hip_main.dat.gz")
    print("/update: File gunzipped.")
    text = text.decode()
    stars = text.split("\n")
    stars = stars[:-1]
    data = {}
    for star in stars:
        number = star[8:14].strip()
        data[number] = star
    data = json.dumps(data)
    with open("hip_main.json", "w") as f:
        f.write(data)
    status = "200 OK"
    responseHeaders = [("Content-type", "application/json")]
    output = json.dumps(["Cache updated."])
    return status, responseHeaders, output

def checkCache():
    """Returns True iff cache exists in current directory."""
    ls = os.listdir('.')
    return "hip_main.json" in ls

class NotInCatalog(Exception):
    pass

class InvalidTime(Exception):
    pass

class InvalidAddress(Exception):
    pass

def rawHIPData(star):
    """Returns strings for raw data in Hipparcos for the star with that HIP number. Data is [HIP number, Right Ascension, Declination, Apparent Magnitude, Parallax, Color Index, Spectral Type]"""
    with open("hip_main.json", "r") as f:
        stars = f.read()
    stars = json.loads(stars)
    try:
        star = stars[star]
    except KeyError:
        raise NotInCatalog
    number = star[8:14].strip()
    rightAscension = star[17:28]
    declination = star[29:40]
    apparentMagnitude = star[41:46].strip()
    parallax = star[79:86].strip()
    color = star[245:251].strip()
    spectralType = star[435:447].strip()
    output = [number, rightAscension, declination, apparentMagnitude, parallax, color, spectralType]
    return output

def _toRadians(angles):
    """Converts list of angles from degrees to radians."""
    import math
    output = []
    for angle in angles:
        output.append(angle * (math.pi/180))
    return output

def _toAltaz(location, time, address):
    """Converts right ascension and declination to altitude-azimuth. Currently non-functional."""
    import pdb
    pdb.set_trace()
    import math
    jd = time.jd
    d = jd - 2451545
    gmst = 18.697374558 + 24.06570982441908*d
    gmst = gmst % 24
    ra, dec, lon, lat = location.ra.to_value(), location.dec.to_value(), address.lon.to_value(), address.lat.to_value()
    lha = (gmst - ra) * 15 + lon
    angles = _toRadians([ra, dec, lon, lat, lha])
    ra, dec, lon, lat, lha = angles[0], angles[1], angles[2], angles[3], angles[4]
    altitude = math.cos(lha)*math.cos(dec)*math.cos(lat) + math.sin(dec)*math.sin(lat)
    altitude = math.asin(altitude)*(180/math.pi)
    azinum, azidem = -math.sin(lha),  math.tan(dec)*math.cos(lat) - math.sin(lat)*math.cos(lha)
    azimuth = math.atan2(azinum, azidem) * (180/math.pi)
    if azimuth < 0:
        azimuth += 360
    location = str(azimuth)+" "+str(altitude)
    return location

def amateur(data):
    """Processes data from rawHIPData to data useful for amateur astronomers."""
    import math
    import astropy.coordinates as coord
    import astropy.units as u
    from astropy.time import Time
    # Error for bad address: coord.name_resolve.NameResolveError
    name = "HIP %s" % data[0]
    ra = data[1]
    dec = data[2]
    ra = ra.split()
    ra = "%sh%sm%ss" % (ra[0],ra[1],ra[2])
    dec = dec.split()
    dec = "%sd%sm%ss" % (dec[0],dec[1],dec[2])
    location = coord.SkyCoord(ra, dec)
    constellation = location.get_constellation()
    """
    try:
        time = Time(time)
    except ValueError:
        raise InvalidTime
    try:
        address = coord.EarthLocation.of_address(address)
    except coord.name_resolve.NameResolveError:
        raise InvalidAddress
    """
    ra = str(location.ra.to_value()) + "\u00b0"
    dec = str(location.dec.to_value()) + "\u00b0"
    appMag = float(data[3])
    if appMag <= 6:
        hard = "naked eye"
    elif appMag <= 10:
        hard = "binoculars"
    else:
        hard = "telescope"
    parallax = float(data[4]) * u.mas
    distance = u.au / math.tan(parallax.decompose().value)
    distance = distance.to("lyr").value
    distance = str(distance) + " ly"
    output = {
        "name": name,
        "constellation": constellation,
        "right ascension": ra,
        "declination": dec,
        "apparent magnitude": str(appMag),
        "requirements to view": hard,
        "distance": distance
    }
    return output

def fromSpectralType(spectralType):
    """Gets info from spectral type."""
    group = None
    if spectralType.startswith("sd"):
        group = "main sequence"
        color = spectralType[2:]
        return group, color
    elif spectralType.startswith("D"):
        group = "white dwarf"
        return group, "white"
    else:
        try:
            color = spectralType[:2]
        except KeyError:
            return "unknown", "unknown"
        rest = spectralType[2:]
        # Code to get the group. It's always at the start of rest.
        if rest.startswith("I"):
            if rest.startswith("II"):
                if rest.startswith("III"):
                    group = "III"
                else:
                    group = "II"
            elif rest.startswith("IV"):
                group = "IV"
            else:
                group = "I"
        elif rest.startswith("V"):
            group = "V"
        else:
            group = ""
        table = {
            "I": "supergiant",
            "II": "giant",
            "III": "giant",
            "IV": "subgiant",
            "V": "main sequence",
            "": "unknown"
        }
        group = table[group]
        return group, color

def professional(data):
    """Processes data from rawHIPData to give data useful to professional astronomers."""
    import math
    import astropy.units as u
    import astropy.constants as consts
    from magnitudewizard import mag_def
    appMag = float(data[3])
    parallax = float(data[4])
    colorIndex = float(data[5])
    spectralType = data[6]
    parallax = 1e-3 * parallax
    distance = 1 / parallax
    absMag = appMag - 5 * math.log10(distance/10)
    fluxAt10pc = mag_def("%s x" % absMag) * (u.W / (u.m**2))
    luminosity = fluxAt10pc * (4*math.pi*(10*u.pc)**2)
    luminosity = luminosity.to("W")
    temperature = 4600 * (1/(0.92*colorIndex+1.7) + 1/(0.92*colorIndex+0.62)) * u.K
    area = luminosity / (consts.sigma_sb * temperature**4)
    radius = (area / (4*math.pi))**(1/2)
    radius = radius.to("Rsun")
    group, colorType = fromSpectralType(spectralType)
    if group == "main sequence":
        luminosity = luminosity.to("Lsun").value
        mass = luminosity**(1/3.5) * u.Msun
        mass = round(mass.value, 1) # This method of finding mass is not very precise.
        mass = "about %s solar masses" % mass
    else:
        mass = "unknown"
    output = {
        "mass": mass,
        "temperature": str(temperature.value) + " K",
        "type": group,
        "absolute magnitude": str(absMag),
        "radius": "VERY ROUGHLY %s solar radii" % str(round(radius.value, 1)),
        "age": "unknown",
        "expolanets": "unknown"
    }
    return output

def infoCore(star):
    """Processes info for star."""
    haveHIPData = checkCache()
    if not haveHIPData:
        # If we don't have the data, we have to get it via /update
        output = ["Go to http://localhost:8888/update"]
        output = json.dumps(output)
        return output
    if star == None:
        output = ["/info?star=X where X is the HIP number desired."]
        output = json.dumps(output)
        return output
    data = rawHIPData(star)
    a = amateur(data)
    p = professional(data)
    output = {
        "For Amateur Astronomers": a,
        "Intrinsic Properties": p
    }
    output = json.dumps(output)
    return output

def info(environ):
    """Wrapper around infoCore. Sends star from query string to infoCore."""
    import urllib.parse
    qs = environ["QUERY_STRING"]
    qs = urllib.parse.parse_qs(qs)
    star = qs.get("star",[""])[0]
    if star == "":
        star = None
    try:
        output = infoCore(star)
        status = "200 OK"
    except NotInCatalog:
        status = "500 Internal Server Error"
        output = json.dumps(["Error: Not a star in catalog"])
    except InvalidAddress:
        status = "500 Internal Server Error"
        output = json.dumps(["Error: Invalid Address"])
    except InvalidTime:
        status = "500 Internal Server Error"
        output = json.dumps(["Error: Invalid Date"])
    responseHeaders = [("Content-type", "application/json")]
    return status, responseHeaders, output

allowed = {
    "/favicon.ico": favicon,
    "/robots.txt": robots,
    "/update": update,
    "/info": info
}

def application(environ, start_response):
    global allowed
    path = environ["PATH_INFO"]
    if path in allowed.keys():
        status, responseHeaders, output = allowed[path](environ)
    elif path == "/":
        status = "200 OK"
        responseHeaders = [("Content-type", "text/html; charset=utf-8")]
        keys = list(allowed.keys())
        output = "<!DOCTYPE html>\n"
        for key in keys:
            output += "<a href=\"{link}\">{link}</a><br>\n".format(link=key)
    else:
        status = "404 Not Found"
        responseHeaders = [("Content-type", "application/json")]
        output = {"error": "Not Found"}
        output = json.dumps(output)
    start_response(status, responseHeaders)
    if type(output) == bytes:
        return [output]
    else:
        return [output.encode()]
