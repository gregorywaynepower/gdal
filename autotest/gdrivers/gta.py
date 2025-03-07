#!/usr/bin/env pytest
###############################################################################
#
# Project:  GDAL/OGR Test Suite
# Purpose:  Test GTA driver
# Author:   Even Rouault <even dot rouault at spatialys.com>
#
###############################################################################
# Copyright (c) 2011, Even Rouault <even dot rouault at spatialys.com>
#
# SPDX-License-Identifier: MIT
###############################################################################


import gdaltest
import pytest

from osgeo import gdal

pytestmark = pytest.mark.require_driver("GTA")

init_list = [
    ("byte.tif", 4672),
    ("gtiff/int8.tif", 1046),
    ("int16.tif", 4672),
    ("uint16.tif", 4672),
    ("int32.tif", 4672),
    ("uint32.tif", 4672),
    ("float32.tif", 4672),
    ("float64.tif", 4672),
    ("cint16.tif", 5028),
    ("cint32.tif", 5028),
    ("cfloat32.tif", 5028),
    ("cfloat64.tif", 5028),
    ("rgbsmall.tif", 21212),
]

###############################################################################
# Test updating existing dataset, check srs, check gt


def test_gta_2():

    src_ds = gdal.Open("data/byte.tif")
    out_ds = gdaltest.gta_drv.CreateCopy("/vsimem/byte.gta", src_ds)
    out_ds = None

    out_ds = gdal.Open("/vsimem/byte.gta", gdal.GA_Update)
    out_ds.GetRasterBand(1).Fill(0)
    out_ds = None

    out_ds = gdal.Open("/vsimem/byte.gta")
    cs = out_ds.GetRasterBand(1).Checksum()
    assert cs == 0, "did not get expected checksum"
    out_ds = None

    out_ds = gdal.Open("/vsimem/byte.gta", gdal.GA_Update)
    out_ds.WriteRaster(0, 0, 20, 20, src_ds.ReadRaster(0, 0, 20, 20))
    out_ds = None

    out_ds = gdal.Open("/vsimem/byte.gta")
    cs = out_ds.GetRasterBand(1).Checksum()
    assert cs == src_ds.GetRasterBand(1).Checksum(), "did not get expected checksum"

    gt = out_ds.GetGeoTransform()
    wkt = out_ds.GetProjectionRef()
    out_ds = None

    expected_gt = src_ds.GetGeoTransform()
    for i in range(6):
        assert gt[i] == pytest.approx(
            expected_gt[i], abs=1e-6
        ), "did not get expected wkt"

    assert wkt == src_ds.GetProjectionRef(), "did not get expected wkt"

    gdaltest.gta_drv.Delete("/vsimem/byte.gta")


###############################################################################
# Test writing and readings GCPs


@pytest.mark.skipif(
    not gdaltest.vrt_has_open_support(),
    reason="VRT driver open missing",
)
def test_gta_3():

    src_ds = gdal.Open("../gcore/data/gcps.vrt")

    new_ds = gdaltest.gta_drv.CreateCopy("/vsimem/gta_3.gta", src_ds)
    new_ds = None

    new_ds = gdal.Open("/vsimem/gta_3.gta")

    assert new_ds.GetGeoTransform() == (
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        1.0,
    ), "GeoTransform not set properly."

    assert new_ds.GetProjectionRef() == "", "Projection not set properly."

    assert (
        new_ds.GetGCPProjection() == src_ds.GetGCPProjection()
    ), "GCP Projection not set properly."

    gcps = new_ds.GetGCPs()
    expected_gcps = src_ds.GetGCPs()
    assert len(gcps) == len(expected_gcps), "GCP count wrong."

    new_ds = None

    gdaltest.gta_drv.Delete("/vsimem/gta_3.gta")


###############################################################################
# Test band metadata


def test_gta_4():

    src_ds = gdal.GetDriverByName("MEM").Create("", 1, 1, 17)
    src_ds.GetRasterBand(1).Fill(255)
    src_ds.GetRasterBand(1).ComputeStatistics(False)
    src_ds.GetRasterBand(1).SetNoDataValue(123)
    src_ds.GetRasterBand(1).SetCategoryNames(["a", "b"])
    src_ds.GetRasterBand(1).SetOffset(2)
    src_ds.GetRasterBand(1).SetScale(3)
    src_ds.GetRasterBand(1).SetUnitType("custom")
    src_ds.GetRasterBand(1).SetDescription("description")
    for i in range(17):
        if i != gdal.GCI_PaletteIndex:
            src_ds.GetRasterBand(i + 1).SetColorInterpretation(i)

    new_ds = gdaltest.gta_drv.CreateCopy("/vsimem/gta_4.gta", src_ds)
    new_ds = None

    new_ds = gdal.Open("/vsimem/gta_4.gta")
    band = new_ds.GetRasterBand(1)
    assert band.GetNoDataValue() == 123, "did not get expected nodata value"
    assert band.GetMinimum() == 255, "did not get expected minimum value"
    assert band.GetMaximum() == 255, "did not get expected maximum value"
    assert band.GetCategoryNames() == ["a", "b"], "did not get expected category names"
    assert band.GetOffset() == 2, "did not get expected offset value"
    assert band.GetScale() == 3, "did not get expected scale value"
    assert band.GetUnitType() == "custom", "did not get expected unit value"
    assert band.GetDescription() == "description", "did not get expected description"
    for i in range(17):
        if i != gdal.GCI_PaletteIndex:
            assert (
                new_ds.GetRasterBand(i + 1).GetColorInterpretation() == i
            ), "did not get expected color interpretation " "for band %d" % (i + 1)

    new_ds = None

    gdaltest.gta_drv.Delete("/vsimem/gta_4.gta")


###############################################################################
# Test compression algorithms


def test_gta_5():

    src_ds = gdal.Open("data/byte.tif")

    compress_list = [
        "NONE",
        "BZIP2",
        "XZ",
        "ZLIB",
        "ZLIB1",
        "ZLIB2",
        "ZLIB3",
        "ZLIB4",
        "ZLIB5",
        "ZLIB6",
        "ZLIB7",
        "ZLIB8",
        "ZLIB9",
    ]

    for compress in compress_list:
        out_ds = gdaltest.gta_drv.CreateCopy(
            "/vsimem/gta_5.gta", src_ds, options=["COMPRESS=" + compress]
        )
        del out_ds

    gdaltest.gta_drv.Delete("/vsimem/gta_5.gta")


@pytest.mark.parametrize(
    "filename,checksum",
    init_list,
    ids=[tup[0].split(".")[0] for tup in init_list],
)
@pytest.mark.require_driver("GTA")
def test_gta_create(filename, checksum):
    if filename != "gtiff/int8.tif":
        filename = "../../gcore/data/" + filename
    ut = gdaltest.GDALTest("GTA", filename, 1, checksum, options=[])
    ut.testCreateCopy()
