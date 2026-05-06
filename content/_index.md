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
  - block: collection
    id: news
    content:
      title: Recent News
      subtitle: ''
      text: ''
      # Page type to display. E.g. post, talk, publication...
      page_type: blog
      # Choose how many pages you would like to display (0 = all pages)
      count: 10
      # Filter on criteria
      filters:
        author: ''
        category: ''
        tag: ''
        exclude_featured: false
        exclude_future: false
        exclude_past: false
        publication_type: ''
      # Choose how many pages you would like to offset by
      offset: 0
      # Page order: descending (desc) or ascending (asc) date.
      order: desc
    design:
      # Choose a layout view
      view: article-grid
      columns: 3
      # Reduce spacing
      spacing:
        padding: [0, 0, 0, 0]
#  - block: team-showcase
#    content:
#      title: Meet Our Team
#      subtitle: World-class researchers advancing science
#      text: Our diverse team brings together expertise from multiple disciplines.
#      user_groups:
#        - Principal Investigators
#        - Postdoctoral Researchers
#        - PhD Students
#        - name: Alumni          # optional per-group sort override
#          sort_by: graduation_year
#          sort_ascending: false
#      sort_by: 'graduation_year' # legacy 'Params.' prefix optional
#      sort_ascending: false
#      #cta:
#      #  text: Join Our Team
#      #  url: /opportunities
#      #  icon: user-plus
#    design:
#      show_role: true
#      show_organizations: true
#      show_interests: true
#      max_interests: 3   # set 0 to hide interests even if provided
#      align: center      # or "left" to align header + CTA left
#      max_columns: 4     # 2, 3, or 4
#      show_social: true
#      show_empty_groups: false # show a placeholder when a group has no members
#      # Section background color (CSS class)
#      css_class: "bg-gray-50 dark:bg-gray-900"

#  - block: markdown
#    content:
#      title: '📚 My Research'
#      subtitle: ''
#      text: |-
#        Use this area to speak to your mission. I'm a research scientist in the Moonshot team at DeepMind. I blog about machine learning, #deep learning, and moonshots.

#        I apply a range of qualitative and quantitative methods to comprehensively investigate the role of science and technology in the economy.

#        Please reach out to collaborate 😃
#    design:
#      columns: '1'
---

#  - block: resume-biography-3
#    content:
#      # Choose a user profile to display (a folder name within `content/authors/`)
#      username: me
#      text: ''
#      # Show a call-to-action button under your biography? (optional)
#      button:
#        text: Download CV
#        url: uploads/resume.pdf
#      headings:
#        about: ''
#        education: ''
#        interests: ''
#    design:
#      # Use the new Gradient Mesh which automatically adapts to the selected theme colors
#      background:
#        gradient_mesh:
#          enable: true
#
#      # Name heading sizing to accommodate long or short names
#      name:
#        size: md # Options: xs, sm, md, lg (default), xl

#      # Avatar customization
#      avatar:
#        size: medium # Options: small (150px), medium (200px, default), large (320px), xl (400px), xxl (500px)
#        shape: circle # Options: circle (default), square, rounded




