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
        size: large # Options: small (150px), medium (200px, default), large (320px), xl (400px), xxl (500px)
        shape: square # Options: circle (default), square, rounded

  - block: markdown
    id: talks
    content:
      title: News
      text: |
        <img src="/news/new-phd-position/featured.png" alt="A lattice of linked robotic units" loading="lazy">

        ## New PhD Position: Embodying Intelligence in Robotic Materials

        Application deadline: **6th November 2026**.

        [Read about the PhD position](/positions/).

        ---

        <img src="/news/twistedfibrenews/featured.png" alt="Twisted optical fibres research featured in Nature Photonics" loading="lazy">

        ## Twisted optical fibres on the cover of Nature Photonics

        Our work on *Twisted Optical Fibres as Photonic Topological Insulators* has been featured on the [cover of Nature Photonics](https://www.nature.com/articles/s41566-026-01848-9), with a [commentary by Michael Rechtsman](https://www.nature.com/articles/s41566-026-01858-7).

        **Associated publication:** [Twisted Optical Fibres as Photonic Topological Insulators](/publications/twisted-optical-fibres-as-photonic-topological-insulators/).

        ---

        <img src="/news/nonreciprocalbucklingnews/featured.png" alt="Nonreciprocal buckling research featured in PNAS" loading="lazy">

        ## Nonreciprocal buckling on the cover of PNAS

        Our work is out now in [PNAS](https://www.pnas.org/toc/pnas/123/11).

        **Associated publication:** [Nonreciprocal Buckling Makes Active Filaments Polyfunctional](/publications/nonreciprocal-buckling-makes-active-filaments-polyfunctional/).

        ---

        <img src="/news/moreislessnews/featured.png" alt="Research on unpercolated active solids" loading="lazy">

        ## More is less featured in Physics Viewpoint

        *More Is Less in Unpercolated Active Solids* is featured in Physics Viewpoint, with [commentary by Tzer Han Tan](https://physics.aps.org/articles/v19/49). Thanks Tzer Han!

        **Associated publication:** [More Is Less in Unpercolated Active Solids](/publications/more-is-less-in-unpercolated-active-solids/).

---
