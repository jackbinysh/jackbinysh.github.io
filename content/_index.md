---
# Leave the homepage title empty to use the site title
title: ''
summary: ''
date: 2022-10-24
type: landing

sections:
  - block: resume-biography-3
    content:
      # Choose a user profile to display (a folder name within `content/authors/`)
      username: me
      text: ''
      # Show a call-to-action button under your biography? (optional)
      #button:
      #  text: Download CV
      #  url: uploads/resume.pdf
      headings:
        #about: 'We study the mechanics of advanced materials for smarter soft robots. '
        about: 'We study the mechanics of advanced materials for smarter soft robots. '
        education: ''
        interests: ''
    design:
      # Use the new Gradient Mesh which automatically adapts to the selected theme colors
      background:
        gradient_mesh:
          enable: false

      # Name heading sizing to accommodate long or short names
      name:
        size: md # Options: xs, sm, md, lg (default), xl

      # Avatar customization
      avatar:
        size: xl # Options: small (150px), medium (200px, default), large (320px), xl (400px), xxl (500px)
        shape: square # Options: circle (default), square, rounded

  - block: collection
    id: talks
    content:
      page_type: news # where to search in teh file system 
      title: News
    design:
      view: article-grid
      # Choose a layout view
      columns: 3
      show_categories: false
      show_date: false       # Toggle the publication date
      show_read_time: false   # Toggle "X min read"
      show_read_more: false  # Show/hide the "Read more" link
      fill_image: true       # When true, the image covers the top of the card

  
---
