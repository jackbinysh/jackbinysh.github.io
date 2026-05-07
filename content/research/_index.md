---
title: "Research"
date: 2022-10-24
type: landing
sections:
  - block: collection
    id: news
    content:
      title: Research
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
      show_categories: false
      show_date: false       # Toggle the publication date
      show_read_time: false   # Toggle "X min read"
      show_read_more: false  # Show/hide the "Read more" link
      fill_image: true       # When true, the image covers the top of the card
      css_class: "no-card-hover"

      # Reduce spacing
      spacing:
        padding: [0, 0, 0, 0]

---