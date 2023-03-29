---
{{- /*
[Create a New Archetype Template](https://gohugo.io/content-management/archetypes/#create-a-new-archetype-template)
[Site Variables](https://gohugo.io/variables/site/)
[Sample Page.md](https://github.com/adityatelange/hugo-PaperMod/wiki/Installation#sample-pagemd)
*/}}
title: {{ replace .Name "-" " " | title }}
date: {{ .Date }}
draft: true
tags: []
author: {{.Site.Params.author}}
cover:
    useFirstImageIfNone: true
{{- /*
    image: # image path/url
    alt: # alt text
    caption: # display caption under cover
    relative: false # when using page bundles set this to true
    hidden: true # only hide on current single page
*/}}
---

***Summary***

<!--more-->

## Head

content
