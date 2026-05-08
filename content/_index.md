---
# Leave the homepage title empty to use the site title
title: ''
summary: ''
date: 2022-10-24
type: landing

sections:
  - block: hero
    content:
      title: Building aligned AI together
      text: Human-centred research, transparent tooling, and production-ready stacks.
      announcement:
        text: Latest preprint is live
        link:
          text: Read the paper
          url: /publications/rlhf-foundations
      primary_action:
        text: Start a project
        url: '#contact'
        icon: hero/arrow-right
      secondary_action:
        text: View portfolio
        url: /projects/
    design:
      background:
        gradient:
          start: primary-500
          end: secondary-500
        text_color_light: true
  #
  #
  - block: markdown
    content:
      title: 
      text: We are part of the department of Mechanical Engineering at the University of Birmingham. {{< figure src="School-of-Engineering.jpg" title="University of Birmingham" >}}

  - block: collection
    id: talks
    content:
      title: News
      filters:
        folders:
          - news
    design:
      view: article-grid
      # Choose a layout view
      columns: 2
      show_categories: false
      show_date: false       # Toggle the publication date
      show_read_time: false   # Toggle "X min read"
      show_read_more: false  # Show/hide the "Read more" link
      fill_image: true       # When true, the image covers the top of the card
---





