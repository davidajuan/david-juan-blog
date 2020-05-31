---
layout: post
title: "Deploying a Jekyll Site to AWS S3"
categories: technology
---

A few weeks back, the team I was working with on the [Mass Testing Platform]({% post_url 2020-05-11-mass-testing-platform %}) open source project was looking for a simple way to make all of the process documentation we created easily accessible to anyone that wanted to use it.  That is when we started heading down the [GitHub Pages](https://pages.github.com/) path which uses Jekyll under the hood to generate a static site off of markdown files.  You can install Jekyll on your local machine and easily build your site to test changes in your dev environment before pushing them to GitHub.  For that project, we used GitHub Actions as the CI pipeline to give us a little more control and visibility into the build.  After we launched the project, I started looking into using Jekyll for my personal blog and hosting the static site in AWS S3.  

## Setup

Marcos Lombog wrote a really [helpful article](https://medium.com/better-programming/build-a-static-website-with-jekyll-and-automatically-deploy-it-to-aws-s3-using-circle-ci-26c1b266e91f) on building a static site with Jekyll, and deploying it to AWS S3 using CircleCI.  In this article, he walks you through step by step:

1. Getting Jekyll installed locally
2. Building your site locally
3. Setting up your staging and production AWS S3 buckets to host your site
4. Setting up AWS CloudFront distributions to put a CDN in front of your buckets
5. Pushing your local Jekyll site to GitHub
6. Setting up a CircleCI pipeline to automate the build and deployment process for both staging and production
7. Setting up a user in AWS IAM to give CircleCI permission to list/put/delete objects in S3
8. Deploying your site

This article is solid, but I found there were a few additional things I needed to do in order to setup a custom domain that is HTTPS enabled, and fix a few issues that occur with Jekyll when serving from S3.  **So if your end goal is to host a site on a custom domain, then here are a few things to consider before you run through the above tutorial.**

## S3 Bucket Naming

When using a custom domain name to direct traffic to S3, I recommend naming your production AWS S3 bucket the same thing as your domain.  The name for your staging S3 bucket won't matter, unless you want to have a custom domain name for that bucket as well.  S3 buckets are a unique namespace, so you may as well secure both the bare and www bucket names in advance.  I secured "davidjuan.com" and "www.davidjuan.com" to give me options if I didn't want to use CloudFront to direct traffic in the future.  If you wanted to skip the CDN and just use a custom domain manged in AWS Route53 to direct traffic to S3, then the bucket name needs to be the same as the domain.  There is some helpful [documentation from AWS](https://docs.aws.amazon.com/AmazonS3/latest/user-guide/redirect-website-requests.html) that walks you through setting this up, and an alternate version of the above tutorial that walks you through [setting up a Jekyll/CircleCI/S3 site without the CDN](http://jamesrcounts.com/guides/hello-world/publish-jekyll-site-to-s3-with-circleci.html).

## Setting up HTTPS

You will need to install an SSL cert in order to have CloudFront serve HTTPS requests to your S3 bucket if you're using a custom domain.  Before setting up your CloudFront distribution, request an SSL cert for your domain using AWS Certificate Manager.  It's pretty straight forward, and AWS has great [documentation on the process](https://docs.aws.amazon.com/acm/latest/userguide/gs-acm-request-public.html).  Make sure to include both the bare domain and the www domain in your request.  When setting up your CloudFront distribution, make sure the View Protocol Policy setting is set to "HTTP or HTTPS", otherwise HTTP requests will be blocked rather than being redirected to HTTPS.  During the setup, select the "Custom SSL Certificate" option, and choose the certificate you created.  You can continue with the rest of the steps in the original tutorial.

## Configuring DNS

To direct your custom domain to the CloudFront distribution you setup, you will need to create two A Records (one for the bare domain, and one for www), and select your CloudFront Distribution as the Alias Target for both.

## Fix Broken Post Links

This is actually not specific to using a custom domain, and is an issue that you will run into when using the CircleCI script in the tutorial to build and deploy your site to S3.  The step below in the script removes the .html extension from your files to clean up your links.

      - run:
          name: Remove .html extension
          command: find _site/ -type f ! -iname 'index.html' -iname '*.html' -print0 | while read -d $'\0' f; do mv "$f" "${f%.html}"; done

The problem is, Jekyll still includes the extension in the Posts links, so you will need to fix that by specifying a permalink without the extension in the _config.yml file.  Just add this line to the file:

    <pre>permalink: /:categories/:year/:month/:day/:title<code>

## Customize your Jekyll Site, and Enjoy!

Jekyll generates all of your sites HTML and CSS files during the build process, so if you make the mistake of editing the files in the _site directory, you will learn that lesson the hard way when all of your changes disappear the next time the site builds.  To include your own HTML, you will need to create a directory named _includes, and place your HTML files there.  You will then need to create _layouts/default.html and reference all of the files in the _includes directory.  For your CSS, create assets/css/style.css, and include this Front Matter at the top of the file:

    ---
    # this ensures Jekyll reads the file to be transformed into CSS later
    # only Main files contain this front matter, not partials.
    ---

If you're using Sass CSS, then you will create a _sass directory to add all of your SCSS files, and reference them in the assets/css/style.css file.

The work that Janina Phillips did on the project site for Mass Testing Platform is an awesome example of what you can do with Jekyll using your own HTML and CSS.  Take a look at the [GitHub repo](https://github.com/QuickenLoans/MassTestingPlatform/tree/master/docs) to get some ideas on how to structure everything.

I think you will be really happy with this whole setup once you're done.  You end up with a developer friendly blog that is maintenance free, cheap to run, and can scale infinitely.  *Even if* you don't ever actually end up writing any content, you will still have fun setting it up.  **Enjoy!**