import https from 'https';
import http from 'http';

import type { KeyedObject, Nullable } from '@/types';

type FetchyThis = {
  baseURL: string;
  headers: KeyedObject; // TODO
  httpAgent: Nullable<http.Agent>;
  httpsAgent: Nullable<https.Agent>;
  options: KeyedObject; // TODO
  privateSetBaseURL: (baseURL: string) => string;
};

interface Options extends RequestInit {
  agent: () => FetchyThis['httpAgent'] | FetchyThis['httpsAgent'];
  searchParams?: KeyedObject;
}

export const DEFAULT_FETCH_HEADERS = {
  Accept: 'application/json',
  'Access-Control-Allow-Origin': '*',
  'Content-Type': 'application/json;charset=UTF-8',
};

const fetchy = (function () {
  const _this: FetchyThis = {
    baseURL: '',
    headers: {
      ...DEFAULT_FETCH_HEADERS,
    },
    httpAgent: null,
    httpsAgent: null,
    options: {
      agent: null,
      searchParams: {},
    },
    privateSetBaseURL: function (baseURL: string) {
      if (baseURL == null || typeof baseURL !== 'string' || baseURL === '') {
        throw new TypeError("fetchy: argument 'baseURL' must be a non-empty string");
      }
      // TODO: should maybe parse 'baseURL' somehow to make sure it's URL safe?
      console.log(`fetchy#privateSetBaseURL: '${baseURL}'`);
      _this.baseURL = baseURL;

      return _this.baseURL;
    },
  };

  /**
   * @description Tests whether a given string is a valid, absolute URL by using parts 1-4
   * of the Regular Expression from {@link https://datatracker.ietf.org/doc/html/rfc3986#appendix-B|RFC 3986, Appendix B}
   */
  const isAbsoluteURL = (reqString: string): boolean => {
    // TODO: this RegEx isn't working :[
    return /^(([^:\/?#]+):)?(\/\/([^\/?#]*))?/im.test(reqString);
  };

  /**
   * @description Determines whether the current context is a browser by testing if
   *  the global `window` variable is defined
   */
  const isFrontend = (): boolean => typeof window !== 'undefined';

  const isHttps = (): boolean => _this.baseURL.includes('https');

  /**
   * @description Resolves and forwards arguments to correct `fetch` reference
   */
  const $fetch: Window['fetch'] = (...args) =>
    isFrontend() ? window.fetch(...args) : global.fetch(...args);

  function appendSearchParamsToUrl(
    url: string,
    searchParams: Nullable<KeyedObject>,
  ): string {
    if (searchParams == null || Object.keys(searchParams).length < 1) {
      return url;
    }

    let hasFirstParam = url.indexOf('?') === -1;

    return Object.entries(searchParams).reduce(function (finalUrl, paramEntry) {
      if (paramEntry[1] === '') {
        return finalUrl;
      }

      const [key, value] = paramEntry;

      if (!hasFirstParam) {
        finalUrl += `&${key}=${value}`;
      } else {
        finalUrl += `?${key}=${value}`;
        hasFirstParam = true;
      }

      return finalUrl;
    }, `${url}`);
  }

  async function doFetch(urlOrPath: string, options: KeyedObject = {}) {
    if (urlOrPath == null || typeof urlOrPath !== 'string' || urlOrPath === '') {
      throw new TypeError("fetchy: argument 'urlOrPath' must be a non-empty string");
    }

    console.log(
      'fetchy#doFetch:\n',
      `    urlOrPath === ${urlOrPath}\n`,
      `    _this.baseURL === ${_this.baseURL}\n`,
      `    isAbsoluteURL === ${isAbsoluteURL(urlOrPath)}\n`,
    );
    if (!_this.baseURL && !isAbsoluteURL(urlOrPath)) {
      // TODO: better solution for this...?
      const { protocol, host } = isFrontend()
        ? window.location
        : { protocol: 'https', host: 'nlp-ssa.dev' };
      _this.privateSetBaseURL(`${protocol}//${host}`);
    }

    // TODO: this feels... inefficient?
    const headersFromOptions = options.headers || {};
    delete options.headers;

    const combinedOptions: Options = {
      ..._this.options,
      ...options,
      agent: isHttps() ? () => _this.httpsAgent : () => _this.httpAgent,
      headers: new Headers({
        ..._this.headers,
        ...headersFromOptions,
      }),
    };

    const requestUrl = appendSearchParamsToUrl(
      urlOrPath,
      combinedOptions.searchParams as Nullable<KeyedObject>,
    );

    // TODO: more to do here...?
    console.log(`fetchy: making request to '${requestUrl}'`);
    return $fetch(requestUrl, combinedOptions);
  }

  function $doGET(urlOrPath: string, options = {}) {
    const getOptions = {
      ...options,
      method: 'GET',
    };
    return doFetch(urlOrPath, getOptions);
  }

  function $doPOST(urlOrPath: string, { bodyJson = {}, options = {} }) {
    const postOptions = {
      ...options,
      body: JSON.stringify(bodyJson),
      method: 'POST',
    };
    return doFetch(urlOrPath, postOptions);
  }

  function $doPUT(urlOrPath: string, { bodyJson = {}, options = {} }) {
    const putOptions = {
      ...options,
      body: JSON.stringify(bodyJson),
      method: 'PUT',
    };
    return doFetch(urlOrPath, putOptions);
  }

  function $addHeaders(headers: KeyedObject) {
    for (const [key, value] of Object.entries(headers)) {
      _this.headers[key] = value;
    }
    return _this.headers;
  }

  function $getHeaders() {
    return _this.headers;
  }

  function $getBaseURL(): string {
    return _this.baseURL;
  }

  function $setBaseURL(baseURL: string) {
    // TODO: not sure how I feel about this behavior...
    if (!_this.baseURL) {
      _this.baseURL = baseURL;
    }
    return _this.baseURL;
  }

  return {
    _fetch: $fetch,
    get: $doGET,
    post: $doPOST,
    put: $doPUT,
    // delete: $doDELETE,
    addHeaders: $addHeaders,
    getHeaders: $getHeaders,
    getBaseURL: $getBaseURL,
    setBaseURL: $setBaseURL,
  };
})();

export default fetchy;
