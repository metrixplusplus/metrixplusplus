# -*- coding: utf-8 -*-
#
#    Metrix++, Copyright 2009-2019, Metrix++ Project
#    Link: https://github.com/metrixplusplus/metrixplusplus
#
#    This file is a part of Metrix++ Tool.
#
"""
This package implements Halstead's and Oman's metrics

- halstead_base.py:
  calculates Halstead's basic metrics n1,n2,N1,N2 values
- halstead.py:
  uses n1,n2,N1,N2 from halstead_base
  to calculate Halstead's advanced metrics,
  - program length N
  - vocabulary n
  - program volume V
  - difficulty level D
  - program level L
  - implementation effort E
  - implementation time T
  - delivered bugs B
- maintainability.py:
  uses Halstead's program volume, McCabes cyclomatic complexity
  and several LOC metrics
  to calculate Oman's maintainability indices
  - average percent of lines of comments per Module perCM
  - Maintainability Index without comments MIwoc
  - Maintainability Index comment weight MIcw
  - Summary Maintainability Index MIsum = MIwoc+MIcw

An overview is found on https://www.verifysoft.com/en_halstead_metrics.html
and https://www.verifysoft.com/en_maintainability.html

A discussion of software metrics (esp. Halstead and Oman): https://core.ac.uk/download/pdf/216048382.pdf

A detailed explanation with example is found on http://www.verifysoft.com/de_cmtpp_mscoder.pdf (german)
"""
