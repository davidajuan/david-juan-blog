---
layout: home
title: David Juan — Engineering leadership, product & systems
tagline: Leading digital transformation through engineering excellence.
description: Engineering leadership, product strategy, and practical lessons from large-scale platform delivery.
image: /assets/images/social-card.svg
image_alt: "David Juan — engineering leader"
---

<picture>
	<source type="image/webp" srcset="/assets/images/hero-1200.webp 1200w, /assets/images/hero-800.webp 800w, /assets/images/hero-400.webp 400w" sizes="(max-width: 800px) 100vw, 1200px">
	<img src="/assets/images/hero-800.jpg" alt="David Juan — engineering leader outdoors" width="1200" height="600" loading="lazy" style="max-width:100%;height:auto;">
</picture>

## I'm a technologist from Detroit writing about engineering leadership, product strategy, and life. For the most recent updates, check my [LinkedIn](https://www.linkedin.com/in/davidajuan/){:target="_blank" rel="noopener noreferrer"}.

---

## Latest posts
<ul class="posts-list">
	{% for post in site.posts limit:5 %}
		<li>
			<a href="{{ post.url | relative_url }}">{{ post.title }}</a>
			<small>{{ post.date | date: "%b %-d, %Y" }}</small>
		</li>
	{% endfor %}
</ul>

