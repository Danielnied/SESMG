---
title: 'Spreadsheet Energy System Model Generator (SESMG): A tool for the optimization of urban energy systems'
tags:
  - Python
  - Energy System Modeling
  - Urban Energy System
  - Optimization
  - Multi-Energy Systems
authors:
  - name: Christian Klemm
    corresponding: true # (This is how to denote the corresponding author)
    orcid: 0000-0003-0801-4178
    affiliation: "1, 2"
  - name: Gregor Becker
    orcid: 0000-0001-8803-6873
    affiliation: 1
  - name: Janik Budde
    orcid: 0000-0002-1617-5900
    affiliation: 1
  - name: Jan Tockloth
    orcid: 0000-0003-2582-1043
    affiliation: 1
  - name: Peter Vennemann
    orcid: 0000-0002-0767-5014
    affiliation: 1
affiliations:
 - name: Münster University of Applied Sciences, Department of Energy, Building Services and Environmental Engineering, Germany
   index: 1
 - name: Europa-Universität Flensburg, Department of Energy and Environmental Management, Germany 
   index: 2
date: 30 April 2023
bibliography: paper.bib

---
# Summary

The Spreadsheet Energy System Model Generator (SESMG) is a tool for modeling and optimizing energy systems with a focus on urban systems. The SESMG has a very low barrier to entry, requiring no programming skills and using spreadsheets to define individual models. It includes advanced modeling features such as the application of the multi-energy system (MES) approach, multi-objective optimization, model-based methods for reducing computational requirements, and automated conceptualization and result processing of urban energy systems with high spatial resolution. Due to the good usability and the applied modeling methods, urban energy systems can be modeled and optimized with comparatively low effort.

# Statement of need
Planning and optimal design of urban energy systems is becoming increasingly complex [@Zhang.2018] due to sector coupling, the use of decentralized renewable energy sources with volatile production, the use of diverse energy storage systems, the growing importance of new sectors such as hydrogen, as well as the increasing relevance of multiple planning objectives. In this context, urban energy systems are defined as “the combined process of acquiring and using energy in a given spatial entity with a high density and differentiation of residents, buildings, commercial sectors, infrastructure, and energy sectors (e.g., heat, electricity, fuels)” [@Klemm.Indicators]. Traditionally, such systems are designed by simulating and comparing a limited number of pre-defined energy supply scenarios, without using optimization methods. Individual buildings, consumption sectors, or energy sectors are rarely planned and designed holistically, but rather separately from each other [@Lukszo.2018]. Finally, planning processes are often driven by financial interests only, rather than considering additional planning objectives such as minimizing greenhouse gas emissions, or final energy demand. To fully exploit all synergies and to avoid conflicting interests of increasingly entangled energy systems [@Pfenninger.2014], it is necessary to carry out holistic planning [@Lukszo.2018]. Therefore, all energy sectors, planning objectives, as well as an entire spatial entity should be considered within a holistic analysis [@UN.2015]. Thereby, not only certain, but all theoretically possible supply scenarios should be compared by using optimization algorithms [@DeCarolis.2017] in order to ensure that those scenarios are identified that allow the minimization of the planning objectives by a given ratio [@Klemm.Indicators]. All these demands on planning and optimization methods result in increasingly high computing requirements, especially in run-time and random access memory (RAM) [@Klemm.2023]. To limit the necessary computing capacities to an acceptable extend, modelers must make decisions regarding the temporal and spatial resolution of the system. Alternatively, model-based or solver-based methods can be used to reduce the computational requirements [@Cao.2019], with only slight differences in the quality of the results.

The Spreadsheet Energy System Model Generator (SESMG) is based on the Open Energy Modeling Framework (oemof) [@oemof]. Combined with its own functionalities, the SESMG meets the above described modeling challenges, by

* considering the **multi-energy system (MES)** approach [@Mancarella.2016], 

* carrying out **multi-objective optimization** by using the epsilon-constraint-method [@Mavrotas.2009], and by

* enabling high spatial resolution results through the applicability of **model-based** methods for the **reduction of computational effort** [@Klemm.2023].

The SESMG enables the optimization of multi-sectoral and spatial synergies of urban energy systems of up to 1000 buildings. Through the multi-criteria result output in the form of a Pareto front, transformation processes between status quo, cost minimized and emission minimized target scenarios can be identified.

Finally, the SESMG comes with several advantages regarding user-friendliness compared to other modeling tools due to

* applicability **without any programming knowledge**,

* **automatic conceptualization** of individual urban energy systems with any size,

* **automatic result processing** and vizualization of complex relationships in form of system graphs, pareto-fronts, energy amount diagrams, capacity diagrams, and more, as well as

* a set of **standard (but still customizable) technical and economic modeling parameters** including description and references.

The SESMG comes with a [detailed documentation](https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/ "detailed documentation"), including step-by-step instructions, explanations of all modeling methods and troubleshooting with known application errors. In addition, the documentation includes an ongoing list of peer review publications, conference proceedings, study works, research projects, and other publications related to the SESMG.

# Acknowledgements
The authors would like to thank the oemof user and developer community for the development of the Open Energy Modeling Framework and for discussions regarding the development of the SESMG. This research has been conducted within the R2Q project, funded by the German Federal Ministry of Education and Research (BMBF), grant number 033W102A.

# References

