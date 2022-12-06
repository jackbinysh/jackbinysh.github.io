---
layout: page
permalink: /publications/
title: publications
description: 
years: [2022,2020,2019,2018]
months: [dec,nov,oct,sept,aug,jul,jun,may,apr,mar,feb,jan]
nav: true
---
<!-- _pages/publications.md -->
<div class="publications">

{%- for y in page.years %}
  <!--  <h2 class="year">{{y}}</h2> -->
    {% bibliography -f papers -q @*[year={{y}}]* %}
{% endfor %}

</div>
