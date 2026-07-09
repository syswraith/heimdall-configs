## Configuration Reference

Heimdall uses YAML configuration files to define how each service should be queried and parsed. Each config file represents a single service (e.g. `instagram.yaml`, `leetcode.yaml`).

Configs are organized by category in the default configs directory at `~/.config/heimdall/heimdall-configs/`:

```
heimdall-configs/
├── social_media/
│   ├── instagram.yaml
│   ├── snapchat.yaml
│   └── ...
├── development/
│   ├── leetcode.yaml
│   └── ...
├── gaming/
│   └── ...
└── community/
    └── ...
```

The filename (without extension) becomes the service name displayed in output (e.g. `instagram.yaml` → `instagram`). The subdirectory name becomes the category.

### Config Fields

| Field          | Type                | Required | Default          | Description                                                                                                                                                                                                                                                             |
| -------------- | ------------------- | -------- | ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `path`         | `string`            | **Yes**  | —                | The URL to request. Use `%s` as a placeholder for the username (e.g. `https://example.com/users/%s`). The placeholder is substituted at runtime with the target username.                                                                                               |
| `mode`         | `string`            | **Yes**  | —                | The fetching and parsing strategy to use. Determines how the URL is requested and how the response is parsed. See [Modes](#modes) below for all options.                                                                                                                |
| `method`       | `string`            | No       | `GET`            | The HTTP method to use for the request. Supported values: `GET`, `POST`.                                                                                                                                                                                                |
| `body`         | `string`            | No       | `""`             | The request body, used with `POST` requests. Use `%s` as a placeholder for the username. Commonly used for GraphQL queries.                                                                                                                                             |
| `content_type` | `string`            | No       | `""`             | Sets the `Content-Type` header for the request. Typically `application/json` for JSON/GraphQL APIs.                                                                                                                                                                     |
| `headers`      | `map[string]string` | No       | `{}`             | Additional HTTP headers to include with the request. These are merged with the default headers (User-Agent, Accept, Accept-Language). Custom headers override defaults if keys conflict.                                                                                |
| `cookies`      | `map[string]string` | No       | `{}`             | Cookies to attach to the request as key-value pairs. For HTTP-based modes, they are added as `Cookie` headers. For browser modes, they are set via CDP before navigation.                                                                                               |
| `category`     | `string`            | No       | Auto-detected    | The category for this service (e.g. `social_media`, `development`). When using the default configs directory, this is automatically set from the subdirectory name. Only needed in standalone config files.                                                             |
| `timeout`      | `int`               | No       | `0` (no timeout) | Request timeout in seconds. Applies to HTTP client timeouts for `JSON`, `HTTP`, and `OPENGRAPH` modes.                                                                                                                                                                  |
| `sleep`        | `int`               | No       | `0`              | Time to wait (in seconds) after the browser navigates to the page before extracting content. Only used in browser modes (`HEADLESS`, `HEADED`, `HEADLESS_JSON`, `HEADED_JSON`). Useful for pages that load content dynamically via JavaScript.                          |
| `container`    | `string`            | No       | `""`             | A CSS selector that narrows the HTML scope for selector extraction. All `selectors` are evaluated within this container element. Only used in `HTTP` and browser HTML modes. Example: `#main`, `body`, `div.profile`.                                                   |
| `selectors`    | `map[string]string` | No       | `{}`             | A map of label → selector pairs used to extract specific data fields from the response. The label is the output key shown in results. The selector format depends on the mode — see [Selectors](#selectors) below.                                                      |
| `redirects_to` | `string`            | No       | `""`             | A URL that indicates a failed lookup. If the final URL after redirects matches this value, the profile is considered not found. Useful for services that redirect to a homepage instead of returning an error. Comparison ignores trailing slashes and `www.` prefixes. |

### Modes

The `mode` field determines how Heimdall fetches and parses the response from a service.

| Mode | Description |
|------|-------------|
| `JSON` | Makes a standard HTTP request and parses the response as JSON. Selectors use [GJSON path syntax](https://github.com/tidwall/gjson#path-syntax). Best for REST/GraphQL APIs that return JSON. |
| `HTTP` | Makes a standard HTTP request and parses the response as HTML. Selectors use CSS selectors via [goquery](https://github.com/PuerkitoBio/goquery). Best for server-rendered HTML pages. |
| `HEADLESS` | Launches a headless browser to render the page, then parses the resulting HTML. Uses CSS selectors. Best for JavaScript-heavy pages that don't have an API. |
| `HEADED` | Same as `HEADLESS`, but the browser window is visible. Useful for debugging and development. |
| `HEADLESS_JSON` | Launches a headless browser, but extracts and parses the page content as JSON (reads `document.body.innerText`). Useful for API endpoints that require browser-level headers/cookies/JS to access. |
| `HEADED_JSON` | Same as `HEADLESS_JSON`, but with a visible browser window. Useful for debugging. |
| `OPENGRAPH` | Fetches the page and extracts [OpenGraph](https://ogp.me/) metadata (`og:title`, `og:description`, `og:image`, etc.). Selectors map labels to OG field names. Best for quick profile detection without complex parsing. |

### Selectors

The `selectors` field maps human-readable labels to extraction paths. The format of the selector value depends on the mode:

#### JSON Mode Selectors

Selectors use [GJSON path syntax](https://github.com/tidwall/gjson#path-syntax) to navigate the JSON response.

```yaml
selectors:
  username: data.user.username
  followers: data.user.edge_followed_by.count
  avatar: data.user.profile_pic_url_hd
```

If no selectors are defined, Heimdall dumps all key-value pairs from the JSON response recursively.

#### HTTP / Browser HTML Selectors

Selectors use CSS selectors (via [goquery](https://github.com/PuerkitoBio/goquery)). By default, the text content of the matched element is extracted.

To extract an **attribute** instead of text, append `[attr=<attribute_name>]` to the selector:

```yaml
selectors:
  bio: div.profile > p.bio
  pfp: img.avatar[attr=src]
  link: a.website[attr=href]
```

#### OpenGraph Mode Selectors

Selectors map labels to OpenGraph field names. Available fields:

| Selector Value | OG Property |
|----------------|-------------|
| `title` | `og:title` |
| `type` | `og:type` |
| `description` | `og:description` |
| `site_name` | `og:site_name` |
| `url` | `og:url` |
| `locale` | `og:locale` |
| `determiner` | `og:determiner` |
| `image` | First `og:image` URL |
| `images` | All `og:image` URLs |
| `favicon` | Page favicon URL |

```yaml
selectors:
  title: title
  description: description
  avatar: image
  profile: url
```

#### The `error` Selector

The special `error` selector is used to detect error pages. If the `error` selector matches content in the response, the profile is considered **not found**, even if other selectors match.

```yaml
selectors:
  error: div.error-message
  username: span.username
```

### Default Headers

Heimdall automatically includes the following headers with every request. These can be overridden via the `headers` field.

| Header | Value |
|--------|-------|
| `User-Agent` | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36` |
| `Accept` | `text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8` |
| `Accept-Language` | `en-US,en;q=0.5` |

## Examples

### Basic JSON API

Query a REST API that returns JSON and extract specific fields.

```yaml
# github.yaml
path: https://api.github.com/users/%s
mode: JSON
category: development
timeout: 10
selectors:
  name: name
  bio: bio
  avatar: avatar_url
  followers: followers
  following: following
  repos: public_repos
  location: location
  company: company
```

### GraphQL API with POST

Query a GraphQL endpoint using a POST request with a JSON body.

```yaml
# anilist.yaml
category: community
path: https://graphql.anilist.co
method: POST
content_type: application/json
mode: JSON
timeout: 10
body: '{"query":"query{User(name:\"%s\"){id name about avatar{large} bannerImage}}"}'
selectors:
  id: data.User.id
  about: data.User.about
  avatar: data.User.avatar.large
  banner: data.User.bannerImage
```

### HTML Scraping with Error Detection

Scrape an HTML page with CSS selectors, using `redirects_to` and `error` selectors to detect missing profiles.

```yaml
# codechef.yaml
path: https://codechef.com/users/%s
mode: HTTP
category: development
timeout: 10
container: body
redirects_to: https://www.codechef.com/
selectors:
  error: ''
  rating: '#rating-block-all > div.rating-header.text-center > div.rating-number'
  global-rank: '#rating-block-all > div.rating-ranks > ul > li:nth-child(1) > a > strong'
  country-rank: '#rating-block-all > div.rating-ranks > ul > li:nth-child(2) > a > strong'
```

### Headless Browser with Sleep

Use a headless browser for a JS-heavy page, waiting for content to load.

```yaml
# tryhackme.yaml
path: https://tryhackme.com/api/v2/public-profile?username=%s
mode: HEADLESS_JSON
category: development
timeout: 10
sleep: 5
selectors:
  username: data.username
  level: data.level
  country: data.country
  about: data.about
  rank: data.rank
  streak: data.streak
```

### OpenGraph Metadata

Extract OpenGraph metadata from a profile page for quick detection.

```yaml
# snapchat.yaml
path: https://www.snapchat.com/@%s
mode: OPENGRAPH
category: social_media
timeout: 5
selectors:
  title: title
  description: description
  site: site_name
  profile: url
  avatar: image
  favicon: favicon
```

### Custom Headers

Query an API that requires specific headers for authentication or access.

```yaml
# instagram.yaml
path: https://www.instagram.com/api/v1/users/web_profile_info/?username=%s
mode: JSON
category: social_media
timeout: 10
headers:
  Accept: '*/*'
  x-ig-app-id: '936619743392459'
  referer: https://www.instagram.com/%s/
selectors:
  username: data.user.username
  full_name: data.user.full_name
  biography: data.user.biography
  followers: data.user.edge_followed_by.count
  following: data.user.edge_follow.count
  private: data.user.is_private
  verified: data.user.is_verified
  profile_picture: data.user.profile_pic_url_hd
```
	
