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
  - block: collection
    id: talks
    content:
      title: Recent & Upcoming Talks
      filters:
        folders:
          - events
    design:
      view: card
---





