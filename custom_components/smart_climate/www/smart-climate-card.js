var SmartClimateCard=function(t){"use strict";function e(t,e,s,a){var i,r=arguments.length,o=r<3?e:null===a?a=Object.getOwnPropertyDescriptor(e,s):a;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)o=Reflect.decorate(t,e,s,a);else for(var n=t.length-1;n>=0;n--)(i=t[n])&&(o=(r<3?i(o):r>3?i(e,s,o):i(e,s))||o);return r>3&&o&&Object.defineProperty(e,s,o),o}"function"==typeof SuppressedError&&SuppressedError;const s=globalThis,a=s.ShadowRoot&&(void 0===s.ShadyCSS||s.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,i=Symbol(),r=new WeakMap;let o=class{constructor(t,e,s){if(this._$cssResult$=!0,s!==i)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=e}get styleSheet(){let t=this.o;const e=this.t;if(a&&void 0===t){const s=void 0!==e&&1===e.length;s&&(t=r.get(e)),void 0===t&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),s&&r.set(e,t))}return t}toString(){return this.cssText}};const n=(t,...e)=>{const s=1===t.length?t[0]:e.reduce((e,s,a)=>e+(t=>{if(!0===t._$cssResult$)return t.cssText;if("number"==typeof t)return t;throw Error("Value passed to 'css' function must be a 'css' function result: "+t+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(s)+t[a+1],t[0]);return new o(s,t,i)},c=a?t=>t:t=>t instanceof CSSStyleSheet?(t=>{let e="";for(const s of t.cssRules)e+=s.cssText;return(t=>new o("string"==typeof t?t:t+"",void 0,i))(e)})(t):t,{is:l,defineProperty:d,getOwnPropertyDescriptor:p,getOwnPropertyNames:h,getOwnPropertySymbols:u,getPrototypeOf:v}=Object,m=globalThis,g=m.trustedTypes,f=g?g.emptyScript:"",b=m.reactiveElementPolyfillSupport,y=(t,e)=>t,x={toAttribute(t,e){switch(e){case Boolean:t=t?f:null;break;case Object:case Array:t=null==t?t:JSON.stringify(t)}return t},fromAttribute(t,e){let s=t;switch(e){case Boolean:s=null!==t;break;case Number:s=null===t?null:Number(t);break;case Object:case Array:try{s=JSON.parse(t)}catch(t){s=null}}return s}},_=(t,e)=>!l(t,e),$={attribute:!0,type:String,converter:x,reflect:!1,useDefault:!1,hasChanged:_};Symbol.metadata??=Symbol("metadata"),m.litPropertyMetadata??=new WeakMap;let w=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,e=$){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(t,e),!e.noAccessor){const s=Symbol(),a=this.getPropertyDescriptor(t,s,e);void 0!==a&&d(this.prototype,t,a)}}static getPropertyDescriptor(t,e,s){const{get:a,set:i}=p(this.prototype,t)??{get(){return this[e]},set(t){this[e]=t}};return{get:a,set(e){const r=a?.call(this);i?.call(this,e),this.requestUpdate(t,r,s)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??$}static _$Ei(){if(this.hasOwnProperty(y("elementProperties")))return;const t=v(this);t.finalize(),void 0!==t.l&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(y("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(y("properties"))){const t=this.properties,e=[...h(t),...u(t)];for(const s of e)this.createProperty(s,t[s])}const t=this[Symbol.metadata];if(null!==t){const e=litPropertyMetadata.get(t);if(void 0!==e)for(const[t,s]of e)this.elementProperties.set(t,s)}this._$Eh=new Map;for(const[t,e]of this.elementProperties){const s=this._$Eu(t,e);void 0!==s&&this._$Eh.set(s,t)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){const e=[];if(Array.isArray(t)){const s=new Set(t.flat(1/0).reverse());for(const t of s)e.unshift(c(t))}else void 0!==t&&e.push(c(t));return e}static _$Eu(t,e){const s=e.attribute;return!1===s?void 0:"string"==typeof s?s:"string"==typeof t?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),void 0!==this.renderRoot&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){const t=new Map,e=this.constructor.elementProperties;for(const s of e.keys())this.hasOwnProperty(s)&&(t.set(s,this[s]),delete this[s]);t.size>0&&(this._$Ep=t)}createRenderRoot(){const t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return((t,e)=>{if(a)t.adoptedStyleSheets=e.map(t=>t instanceof CSSStyleSheet?t:t.styleSheet);else for(const a of e){const e=document.createElement("style"),i=s.litNonce;void 0!==i&&e.setAttribute("nonce",i),e.textContent=a.cssText,t.appendChild(e)}})(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,e,s){this._$AK(t,s)}_$ET(t,e){const s=this.constructor.elementProperties.get(t),a=this.constructor._$Eu(t,s);if(void 0!==a&&!0===s.reflect){const i=(void 0!==s.converter?.toAttribute?s.converter:x).toAttribute(e,s.type);this._$Em=t,null==i?this.removeAttribute(a):this.setAttribute(a,i),this._$Em=null}}_$AK(t,e){const s=this.constructor,a=s._$Eh.get(t);if(void 0!==a&&this._$Em!==a){const t=s.getPropertyOptions(a),i="function"==typeof t.converter?{fromAttribute:t.converter}:void 0!==t.converter?.fromAttribute?t.converter:x;this._$Em=a;const r=i.fromAttribute(e,t.type);this[a]=r??this._$Ej?.get(a)??r,this._$Em=null}}requestUpdate(t,e,s,a=!1,i){if(void 0!==t){const r=this.constructor;if(!1===a&&(i=this[t]),s??=r.getPropertyOptions(t),!((s.hasChanged??_)(i,e)||s.useDefault&&s.reflect&&i===this._$Ej?.get(t)&&!this.hasAttribute(r._$Eu(t,s))))return;this.C(t,e,s)}!1===this.isUpdatePending&&(this._$ES=this._$EP())}C(t,e,{useDefault:s,reflect:a,wrapped:i},r){s&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,r??e??this[t]),!0!==i||void 0!==r)||(this._$AL.has(t)||(this.hasUpdated||s||(e=void 0),this._$AL.set(t,e)),!0===a&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(t){Promise.reject(t)}const t=this.scheduleUpdate();return null!=t&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(const[t,e]of this._$Ep)this[t]=e;this._$Ep=void 0}const t=this.constructor.elementProperties;if(t.size>0)for(const[e,s]of t){const{wrapped:t}=s,a=this[e];!0!==t||this._$AL.has(e)||void 0===a||this.C(e,void 0,s,a)}}let t=!1;const e=this._$AL;try{t=this.shouldUpdate(e),t?(this.willUpdate(e),this._$EO?.forEach(t=>t.hostUpdate?.()),this.update(e)):this._$EM()}catch(e){throw t=!1,this._$EM(),e}t&&this._$AE(e)}willUpdate(t){}_$AE(t){this._$EO?.forEach(t=>t.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(t=>this._$ET(t,this[t])),this._$EM()}updated(t){}firstUpdated(t){}};w.elementStyles=[],w.shadowRootOptions={mode:"open"},w[y("elementProperties")]=new Map,w[y("finalized")]=new Map,b?.({ReactiveElement:w}),(m.reactiveElementVersions??=[]).push("2.1.2");const k=globalThis,S=t=>t,A=k.trustedTypes,C=A?A.createPolicy("lit-html",{createHTML:t=>t}):void 0,E="$lit$",z=`lit$${Math.random().toFixed(9).slice(2)}$`,N="?"+z,M=`<${N}>`,P=document,T=()=>P.createComment(""),O=t=>null===t||"object"!=typeof t&&"function"!=typeof t,H=Array.isArray,U="[ \t\n\f\r]",R=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,j=/-->/g,D=/>/g,B=RegExp(`>|${U}(?:([^\\s"'>=/]+)(${U}*=${U}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),F=/'/g,L=/"/g,V=/^(?:script|style|textarea|title)$/i,I=t=>(e,...s)=>({_$litType$:t,strings:e,values:s}),q=I(1),W=I(2),G=Symbol.for("lit-noChange"),Y=Symbol.for("lit-nothing"),J=new WeakMap,K=P.createTreeWalker(P,129);function Z(t,e){if(!H(t)||!t.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==C?C.createHTML(e):e}const Q=(t,e)=>{const s=t.length-1,a=[];let i,r=2===e?"<svg>":3===e?"<math>":"",o=R;for(let e=0;e<s;e++){const s=t[e];let n,c,l=-1,d=0;for(;d<s.length&&(o.lastIndex=d,c=o.exec(s),null!==c);)d=o.lastIndex,o===R?"!--"===c[1]?o=j:void 0!==c[1]?o=D:void 0!==c[2]?(V.test(c[2])&&(i=RegExp("</"+c[2],"g")),o=B):void 0!==c[3]&&(o=B):o===B?">"===c[0]?(o=i??R,l=-1):void 0===c[1]?l=-2:(l=o.lastIndex-c[2].length,n=c[1],o=void 0===c[3]?B:'"'===c[3]?L:F):o===L||o===F?o=B:o===j||o===D?o=R:(o=B,i=void 0);const p=o===B&&t[e+1].startsWith("/>")?" ":"";r+=o===R?s+M:l>=0?(a.push(n),s.slice(0,l)+E+s.slice(l)+z+p):s+z+(-2===l?e:p)}return[Z(t,r+(t[s]||"<?>")+(2===e?"</svg>":3===e?"</math>":"")),a]};class X{constructor({strings:t,_$litType$:e},s){let a;this.parts=[];let i=0,r=0;const o=t.length-1,n=this.parts,[c,l]=Q(t,e);if(this.el=X.createElement(c,s),K.currentNode=this.el.content,2===e||3===e){const t=this.el.content.firstChild;t.replaceWith(...t.childNodes)}for(;null!==(a=K.nextNode())&&n.length<o;){if(1===a.nodeType){if(a.hasAttributes())for(const t of a.getAttributeNames())if(t.endsWith(E)){const e=l[r++],s=a.getAttribute(t).split(z),o=/([.?@])?(.*)/.exec(e);n.push({type:1,index:i,name:o[2],strings:s,ctor:"."===o[1]?it:"?"===o[1]?rt:"@"===o[1]?ot:at}),a.removeAttribute(t)}else t.startsWith(z)&&(n.push({type:6,index:i}),a.removeAttribute(t));if(V.test(a.tagName)){const t=a.textContent.split(z),e=t.length-1;if(e>0){a.textContent=A?A.emptyScript:"";for(let s=0;s<e;s++)a.append(t[s],T()),K.nextNode(),n.push({type:2,index:++i});a.append(t[e],T())}}}else if(8===a.nodeType)if(a.data===N)n.push({type:2,index:i});else{let t=-1;for(;-1!==(t=a.data.indexOf(z,t+1));)n.push({type:7,index:i}),t+=z.length-1}i++}}static createElement(t,e){const s=P.createElement("template");return s.innerHTML=t,s}}function tt(t,e,s=t,a){if(e===G)return e;let i=void 0!==a?s._$Co?.[a]:s._$Cl;const r=O(e)?void 0:e._$litDirective$;return i?.constructor!==r&&(i?._$AO?.(!1),void 0===r?i=void 0:(i=new r(t),i._$AT(t,s,a)),void 0!==a?(s._$Co??=[])[a]=i:s._$Cl=i),void 0!==i&&(e=tt(t,i._$AS(t,e.values),i,a)),e}class et{constructor(t,e){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){const{el:{content:e},parts:s}=this._$AD,a=(t?.creationScope??P).importNode(e,!0);K.currentNode=a;let i=K.nextNode(),r=0,o=0,n=s[0];for(;void 0!==n;){if(r===n.index){let e;2===n.type?e=new st(i,i.nextSibling,this,t):1===n.type?e=new n.ctor(i,n.name,n.strings,this,t):6===n.type&&(e=new nt(i,this,t)),this._$AV.push(e),n=s[++o]}r!==n?.index&&(i=K.nextNode(),r++)}return K.currentNode=P,a}p(t){let e=0;for(const s of this._$AV)void 0!==s&&(void 0!==s.strings?(s._$AI(t,s,e),e+=s.strings.length-2):s._$AI(t[e])),e++}}class st{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,e,s,a){this.type=2,this._$AH=Y,this._$AN=void 0,this._$AA=t,this._$AB=e,this._$AM=s,this.options=a,this._$Cv=a?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode;const e=this._$AM;return void 0!==e&&11===t?.nodeType&&(t=e.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,e=this){t=tt(this,t,e),O(t)?t===Y||null==t||""===t?(this._$AH!==Y&&this._$AR(),this._$AH=Y):t!==this._$AH&&t!==G&&this._(t):void 0!==t._$litType$?this.$(t):void 0!==t.nodeType?this.T(t):(t=>H(t)||"function"==typeof t?.[Symbol.iterator])(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==Y&&O(this._$AH)?this._$AA.nextSibling.data=t:this.T(P.createTextNode(t)),this._$AH=t}$(t){const{values:e,_$litType$:s}=t,a="number"==typeof s?this._$AC(t):(void 0===s.el&&(s.el=X.createElement(Z(s.h,s.h[0]),this.options)),s);if(this._$AH?._$AD===a)this._$AH.p(e);else{const t=new et(a,this),s=t.u(this.options);t.p(e),this.T(s),this._$AH=t}}_$AC(t){let e=J.get(t.strings);return void 0===e&&J.set(t.strings,e=new X(t)),e}k(t){H(this._$AH)||(this._$AH=[],this._$AR());const e=this._$AH;let s,a=0;for(const i of t)a===e.length?e.push(s=new st(this.O(T()),this.O(T()),this,this.options)):s=e[a],s._$AI(i),a++;a<e.length&&(this._$AR(s&&s._$AB.nextSibling,a),e.length=a)}_$AR(t=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);t!==this._$AB;){const e=S(t).nextSibling;S(t).remove(),t=e}}setConnected(t){void 0===this._$AM&&(this._$Cv=t,this._$AP?.(t))}}class at{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,e,s,a,i){this.type=1,this._$AH=Y,this._$AN=void 0,this.element=t,this.name=e,this._$AM=a,this.options=i,s.length>2||""!==s[0]||""!==s[1]?(this._$AH=Array(s.length-1).fill(new String),this.strings=s):this._$AH=Y}_$AI(t,e=this,s,a){const i=this.strings;let r=!1;if(void 0===i)t=tt(this,t,e,0),r=!O(t)||t!==this._$AH&&t!==G,r&&(this._$AH=t);else{const a=t;let o,n;for(t=i[0],o=0;o<i.length-1;o++)n=tt(this,a[s+o],e,o),n===G&&(n=this._$AH[o]),r||=!O(n)||n!==this._$AH[o],n===Y?t=Y:t!==Y&&(t+=(n??"")+i[o+1]),this._$AH[o]=n}r&&!a&&this.j(t)}j(t){t===Y?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}}class it extends at{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===Y?void 0:t}}class rt extends at{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==Y)}}class ot extends at{constructor(t,e,s,a,i){super(t,e,s,a,i),this.type=5}_$AI(t,e=this){if((t=tt(this,t,e,0)??Y)===G)return;const s=this._$AH,a=t===Y&&s!==Y||t.capture!==s.capture||t.once!==s.once||t.passive!==s.passive,i=t!==Y&&(s===Y||a);a&&this.element.removeEventListener(this.name,this,s),i&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){"function"==typeof this._$AH?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}}class nt{constructor(t,e,s){this.element=t,this.type=6,this._$AN=void 0,this._$AM=e,this.options=s}get _$AU(){return this._$AM._$AU}_$AI(t){tt(this,t)}}const ct=k.litHtmlPolyfillSupport;ct?.(X,st),(k.litHtmlVersions??=[]).push("3.3.2");const lt=globalThis;class dt extends w{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){const t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){const e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=((t,e,s)=>{const a=s?.renderBefore??e;let i=a._$litPart$;if(void 0===i){const t=s?.renderBefore??null;a._$litPart$=i=new st(e.insertBefore(T(),t),t,void 0,s??{})}return i._$AI(t),i})(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return G}}dt._$litElement$=!0,dt.finalized=!0,lt.litElementHydrateSupport?.({LitElement:dt});const pt=lt.litElementPolyfillSupport;pt?.({LitElement:dt}),(lt.litElementVersions??=[]).push("4.2.2");const ht=t=>(e,s)=>{void 0!==s?s.addInitializer(()=>{customElements.define(t,e)}):customElements.define(t,e)},ut={attribute:!0,type:String,converter:x,reflect:!1,hasChanged:_},vt=(t=ut,e,s)=>{const{kind:a,metadata:i}=s;let r=globalThis.litPropertyMetadata.get(i);if(void 0===r&&globalThis.litPropertyMetadata.set(i,r=new Map),"setter"===a&&((t=Object.create(t)).wrapped=!0),r.set(s.name,t),"accessor"===a){const{name:a}=s;return{set(s){const i=e.get.call(this);e.set.call(this,s),this.requestUpdate(a,i,t,!0,s)},init(e){return void 0!==e&&this.C(a,void 0,t,e),e}}}if("setter"===a){const{name:a}=s;return function(s){const i=this[a];e.call(this,s),this.requestUpdate(a,i,t,!0,s)}}throw Error("Unsupported decorator location: "+a)};function mt(t){return(e,s)=>"object"==typeof s?vt(t,e,s):((t,e,s)=>{const a=e.hasOwnProperty(s);return e.constructor.createProperty(s,t),a?Object.getOwnPropertyDescriptor(e,s):void 0})(t,e,s)}function gt(t){return mt({...t,state:!0,attribute:!1})}const ft=n`
  :host {
    /* Comfort score colors */
    --sc-comfort-excellent: #4caf50;
    --sc-comfort-good: #2196f3;
    --sc-comfort-fair: #ffc107;
    --sc-comfort-poor: #ff9800;
    --sc-comfort-bad: #f44336;
    --sc-comfort-unknown: #9e9e9e;

    /* HVAC action colors */
    --sc-hvac-heating: #ff5722;
    --sc-hvac-cooling: #2196f3;
    --sc-hvac-fan: #00bcd4;
    --sc-hvac-drying: #ff9800;
    --sc-hvac-idle: #9e9e9e;

    /* Card background - glassmorphism */
    --sc-card-bg: rgba(255, 255, 255, 0.08);
    --sc-card-bg-solid: rgba(32, 33, 36, 0.95);
    --sc-card-border: rgba(255, 255, 255, 0.12);
    --sc-card-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    --sc-backdrop-blur: blur(16px);

    /* Tile backgrounds */
    --sc-tile-bg: rgba(255, 255, 255, 0.05);
    --sc-tile-bg-hover: rgba(255, 255, 255, 0.1);
    --sc-tile-border: rgba(255, 255, 255, 0.08);
    --sc-tile-radius: 16px;

    /* Text colors */
    --sc-text-primary: rgba(255, 255, 255, 0.95);
    --sc-text-secondary: rgba(255, 255, 255, 0.6);
    --sc-text-muted: rgba(255, 255, 255, 0.35);

    /* Font sizes */
    --sc-font-xs: 0.65rem;
    --sc-font-sm: 0.75rem;
    --sc-font-md: 0.875rem;
    --sc-font-lg: 1.1rem;
    --sc-font-xl: 1.5rem;
    --sc-font-xxl: 2rem;

    /* Spacing */
    --sc-space-xs: 4px;
    --sc-space-sm: 8px;
    --sc-space-md: 12px;
    --sc-space-lg: 16px;
    --sc-space-xl: 24px;

    /* Border radius */
    --sc-radius-sm: 8px;
    --sc-radius-md: 12px;
    --sc-radius-lg: 16px;
    --sc-radius-xl: 24px;

    /* Occupied / follow-me glow */
    --sc-glow-occupied: 0 0 12px rgba(255, 193, 7, 0.4);
    --sc-glow-followme: 0 0 16px rgba(33, 150, 243, 0.5);

    /* Priority badge colors */
    --sc-priority-high: #f44336;
    --sc-priority-medium: #ff9800;
    --sc-priority-low: #4caf50;

    /* Section header */
    --sc-section-border: rgba(255, 255, 255, 0.06);
  }

  /* Light mode overrides - triggered by HA theme */
  :host([data-theme='light']) {
    --sc-card-bg: rgba(255, 255, 255, 0.75);
    --sc-card-bg-solid: rgba(248, 249, 250, 0.95);
    --sc-card-border: rgba(0, 0, 0, 0.08);
    --sc-card-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);

    --sc-tile-bg: rgba(255, 255, 255, 0.6);
    --sc-tile-bg-hover: rgba(255, 255, 255, 0.8);
    --sc-tile-border: rgba(0, 0, 0, 0.06);

    --sc-text-primary: rgba(0, 0, 0, 0.87);
    --sc-text-secondary: rgba(0, 0, 0, 0.54);
    --sc-text-muted: rgba(0, 0, 0, 0.3);

    --sc-section-border: rgba(0, 0, 0, 0.06);
  }
`,bt=n`
  /* Heating pulse - warm glow */
  @keyframes sc-pulse-heating {
    0%, 100% {
      box-shadow: 0 0 4px rgba(255, 87, 34, 0.3);
    }
    50% {
      box-shadow: 0 0 12px rgba(255, 87, 34, 0.6);
    }
  }

  .sc-pulse-heating {
    animation: sc-pulse-heating 2s ease-in-out infinite;
  }

  /* Cooling pulse - cool glow */
  @keyframes sc-pulse-cooling {
    0%, 100% {
      box-shadow: 0 0 4px rgba(33, 150, 243, 0.3);
    }
    50% {
      box-shadow: 0 0 12px rgba(33, 150, 243, 0.6);
    }
  }

  .sc-pulse-cooling {
    animation: sc-pulse-cooling 2s ease-in-out infinite;
  }

  /* HVAC action dot pulse */
  @keyframes sc-dot-pulse {
    0%, 100% {
      opacity: 1;
      transform: scale(1);
    }
    50% {
      opacity: 0.6;
      transform: scale(1.3);
    }
  }

  .sc-dot-pulse {
    animation: sc-dot-pulse 1.5s ease-in-out infinite;
  }

  /* Smooth value transition */
  .sc-value-transition {
    transition: color 0.3s ease, transform 0.2s ease;
  }

  /* Collapse/expand transition */
  .sc-collapse {
    overflow: hidden;
    max-height: 0;
    opacity: 0;
    transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1),
                opacity 0.3s ease;
  }

  .sc-collapse.expanded {
    max-height: 2000px;
    opacity: 1;
  }

  /* Fade in animation for tiles */
  @keyframes sc-fade-in {
    from {
      opacity: 0;
      transform: translateY(8px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .sc-fade-in {
    animation: sc-fade-in 0.3s ease forwards;
  }

  /* Slide up for drawer/modal */
  @keyframes sc-slide-up {
    from {
      opacity: 0;
      transform: translateY(100%);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .sc-slide-up {
    animation: sc-slide-up 0.35s cubic-bezier(0.4, 0, 0.2, 1) forwards;
  }

  /* Spin animation for fan */
  @keyframes sc-spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  .sc-spin {
    animation: sc-spin 2s linear infinite;
  }

  /* Shimmer loading effect */
  @keyframes sc-shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }

  .sc-shimmer {
    background: linear-gradient(
      90deg,
      rgba(255, 255, 255, 0.03) 25%,
      rgba(255, 255, 255, 0.08) 50%,
      rgba(255, 255, 255, 0.03) 75%
    );
    background-size: 200% 100%;
    animation: sc-shimmer 1.5s ease-in-out infinite;
  }

  /* Glow effect for occupied rooms */
  @keyframes sc-glow {
    0%, 100% {
      box-shadow: 0 0 8px rgba(255, 193, 7, 0.2);
    }
    50% {
      box-shadow: 0 0 16px rgba(255, 193, 7, 0.4);
    }
  }

  .sc-glow-occupied {
    animation: sc-glow 3s ease-in-out infinite;
  }

  /* Scale button press */
  .sc-press {
    transition: transform 0.1s ease;
  }

  .sc-press:active {
    transform: scale(0.95);
  }
`;function yt(t,e,s,a={}){return t.callService(e,s,a)}function xt(t,e){if(t&&t.states)return t.states[e]}function _t(t){return t.split("_").map(t=>t.charAt(0).toUpperCase()+t.slice(1)).join(" ")}function $t(t,e="°F"){if(null==t||"unknown"===t||"unavailable"===t)return"--"+e;const s="string"==typeof t?parseFloat(t):t;return isNaN(s)?"--"+e:`${Math.round(10*s)/10}${e}`}function wt(t){if(null==t||"unknown"===t||"unavailable"===t)return"--";const e="string"==typeof t?parseFloat(t):t;return isNaN(e)?"--":`${Math.round(e)}`}function kt(t){if(null==t||"unknown"===t||"unavailable"===t)return"var(--sc-comfort-unknown, #9e9e9e)";const e="string"==typeof t?parseFloat(t):t;return isNaN(e)?"var(--sc-comfort-unknown, #9e9e9e)":e>=90?"var(--sc-comfort-excellent, #4caf50)":e>=70?"var(--sc-comfort-good, #2196f3)":e>=50?"var(--sc-comfort-fair, #ffc107)":e>=30?"var(--sc-comfort-poor, #ff9800)":"var(--sc-comfort-bad, #f44336)"}function St(t){if(null==t||"unknown"===t||"unavailable"===t)return"Unknown";const e="string"==typeof t?parseFloat(t):t;return isNaN(e)?"Unknown":e>=90?"Excellent":e>=70?"Good":e>=50?"Fair":e>=30?"Poor":"Bad"}function At(t){if(null==t||"unknown"===t||"unavailable"===t)return"";const e="string"==typeof t?parseFloat(t):t;return isNaN(e)?"":e>.5?"↑":e>.1?"↗":e<-.5?"↓":e<-.1?"↘":"→"}function Ct(t){if(!t)return"";switch(t.toLowerCase()){case"heating":return"🔥";case"cooling":return"❄️";case"idle":return"⏸";case"fan":return"🌀";case"drying":return"💧";case"off":return"⏻";default:return""}}function Et(t){if(!t)return"var(--sc-hvac-idle, #9e9e9e)";switch(t.toLowerCase()){case"heating":return"var(--sc-hvac-heating, #ff5722)";case"cooling":return"var(--sc-hvac-cooling, #2196f3)";case"fan":return"var(--sc-hvac-fan, #00bcd4)";case"drying":return"var(--sc-hvac-drying, #ff9800)";default:return"var(--sc-hvac-idle, #9e9e9e)"}}function zt(t){if(null==t||"unknown"===t||"unavailable"===t)return"--";const e="string"==typeof t?parseFloat(t):t;if(isNaN(e))return"--";if(e<60)return`${Math.round(e)}m`;const s=Math.floor(e/60),a=Math.round(e%60);return a>0?`${s}h ${a}m`:`${s}h`}let Nt=class extends dt{constructor(){super(...arguments),this.roomSlug="",this.compact=!1}_entity(t){return xt(this.hass,`sensor.sc_${this.roomSlug}_${t}`)}_binaryEntity(t){return xt(this.hass,`binary_sensor.sc_${this.roomSlug}_${t}`)}_handleClick(){this.dispatchEvent(new CustomEvent("room-detail-open",{detail:{roomSlug:this.roomSlug},bubbles:!0,composed:!0}))}render(){const t=this._entity("comfort_score"),e=this._entity("temperature"),s=this._entity("humidity"),a=this._entity("target_temperature"),i=this._entity("temperature_trend"),r=this._entity("hvac_action"),o=this._entity("hvac_runtime"),n=this._entity("active_schedule"),c=this._binaryEntity("occupancy"),l=this._binaryEntity("follow_me_target"),d=t?parseFloat(t.state):NaN,p=e?.state,h=s?.state,u=a?.state,v=i?.state,m=r?.state||"idle",g=o?.state,f=n?.state||"",b="on"===c?.state,y="on"===l?.state,x=kt(d),_=isNaN(d)?0:Math.max(0,Math.min(100,d)),$=e?.attributes?.unit_of_measurement||"°F",w=["tile",b?"occupied":"",y?"follow-me":""].filter(Boolean).join(" ");return q`
      <div class="${w}" @click=${this._handleClick}>
        <!-- Comfort gradient overlay -->
        <div
          class="tile-gradient"
          style="background: radial-gradient(circle at top left, ${x}, transparent 70%)"
        ></div>

        <!-- Header: name + occupancy -->
        <div class="tile-header">
          <span class="tile-name">${_t(this.roomSlug)}</span>
          <span
            class="tile-occupancy ${b?"":"vacant"}"
            title="${b?"Occupied":"Vacant"}"
          ></span>
        </div>

        <!-- Temperature -->
        <div class="tile-temp-row">
          <span class="tile-temp">${$t(p,"")}</span>
          <span class="tile-unit">${$}</span>
          <span class="tile-trend">${At(v)}</span>
        </div>

        <!-- Secondary stats: humidity, target -->
        <div class="tile-stats">
          <span class="tile-stat">
            <span class="tile-stat-icon">💧</span>
            ${void 0!==h&&"unknown"!==h?`${Math.round(parseFloat(h))}%`:"--"}
          </span>
          <span class="tile-stat">
            <span class="tile-stat-icon">🎯</span>
            ${$t(u,$)}
          </span>
        </div>

        <!-- Comfort bar -->
        <div class="tile-comfort">
          <div class="tile-comfort-label">
            <span>Comfort</span>
            <span style="color: ${x}">
              ${wt(d)} - ${St(d)}
            </span>
          </div>
          <div class="tile-comfort-bar">
            <div
              class="tile-comfort-fill"
              style="width: ${_}%; background: ${x}"
            ></div>
          </div>
        </div>

        <!-- HVAC action -->
        <div class="tile-hvac">
          <div
            class="tile-hvac-dot ${"idle"!==m&&"off"!==m?"sc-dot-pulse":""}"
            style="background: ${Et(m)}"
          ></div>
          <span class="tile-hvac-text">
            ${Ct(m)}
            ${m.charAt(0).toUpperCase()+m.slice(1)}
          </span>
          <span class="tile-hvac-runtime">${zt(g)}</span>
        </div>

        <!-- Schedule -->
        ${f&&"unknown"!==f&&"unavailable"!==f?q`<div class="tile-schedule">📅 ${f}</div>`:Y}

        <!-- Auxiliary devices slot -->
        <div class="tile-auxiliary">
          <auxiliary-status
            .hass=${this.hass}
            .roomSlug=${this.roomSlug}
          ></auxiliary-status>
        </div>
      </div>
    `}};Nt.styles=[ft,bt,n`
      :host {
        display: block;
      }

      .tile {
        position: relative;
        background: var(--sc-tile-bg);
        border: 1px solid var(--sc-tile-border);
        border-radius: var(--sc-tile-radius);
        padding: var(--sc-space-md);
        cursor: pointer;
        transition: background 0.2s ease, box-shadow 0.3s ease,
          transform 0.15s ease;
        overflow: hidden;
      }

      .tile:hover {
        background: var(--sc-tile-bg-hover);
        transform: translateY(-1px);
      }

      .tile:active {
        transform: scale(0.98);
      }

      /* Gradient overlay based on comfort score */
      .tile-gradient {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        opacity: 0.06;
        pointer-events: none;
        border-radius: var(--sc-tile-radius);
        transition: opacity 0.3s ease;
      }

      .tile:hover .tile-gradient {
        opacity: 0.1;
      }

      /* Occupied glow */
      .tile.occupied {
        box-shadow: var(--sc-glow-occupied);
      }

      /* Follow-me glow */
      .tile.follow-me {
        box-shadow: var(--sc-glow-followme);
        border-color: rgba(33, 150, 243, 0.3);
      }

      /* Header: room name + occupancy */
      .tile-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: var(--sc-space-sm);
      }

      .tile-name {
        font-size: var(--sc-font-md);
        font-weight: 600;
        color: var(--sc-text-primary);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .tile-occupancy {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
        background: var(--sc-comfort-fair);
      }

      .tile-occupancy.vacant {
        background: var(--sc-text-muted);
        opacity: 0.4;
      }

      /* Temperature display */
      .tile-temp-row {
        display: flex;
        align-items: baseline;
        gap: var(--sc-space-xs);
        margin-bottom: var(--sc-space-xs);
      }

      .tile-temp {
        font-size: var(--sc-font-xxl);
        font-weight: 700;
        line-height: 1;
        color: var(--sc-text-primary);
      }

      .tile-trend {
        font-size: var(--sc-font-md);
        color: var(--sc-text-secondary);
      }

      .tile-unit {
        font-size: var(--sc-font-sm);
        color: var(--sc-text-muted);
        font-weight: 400;
      }

      /* Secondary stats row */
      .tile-stats {
        display: flex;
        align-items: center;
        gap: var(--sc-space-md);
        margin-bottom: var(--sc-space-sm);
        font-size: var(--sc-font-xs);
        color: var(--sc-text-secondary);
      }

      .tile-stat {
        display: flex;
        align-items: center;
        gap: 3px;
      }

      .tile-stat-icon {
        opacity: 0.6;
      }

      /* Comfort bar */
      .tile-comfort {
        margin-bottom: var(--sc-space-sm);
      }

      .tile-comfort-label {
        display: flex;
        justify-content: space-between;
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
        margin-bottom: 3px;
      }

      .tile-comfort-bar {
        width: 100%;
        height: 4px;
        background: rgba(255, 255, 255, 0.06);
        border-radius: 2px;
        overflow: hidden;
      }

      .tile-comfort-fill {
        height: 100%;
        border-radius: 2px;
        transition: width 0.6s ease, background-color 0.3s ease;
      }

      /* HVAC action row */
      .tile-hvac {
        display: flex;
        align-items: center;
        gap: var(--sc-space-xs);
        font-size: var(--sc-font-xs);
        color: var(--sc-text-secondary);
        margin-bottom: var(--sc-space-xs);
      }

      .tile-hvac-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        flex-shrink: 0;
      }

      .tile-hvac-text {
        flex: 1;
      }

      .tile-hvac-runtime {
        color: var(--sc-text-muted);
      }

      /* Schedule label */
      .tile-schedule {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: var(--sc-space-xs);
      }

      /* Auxiliary slot */
      .tile-auxiliary {
        margin-top: var(--sc-space-xs);
      }

      /* Compact mode */
      :host([compact]) .tile {
        padding: var(--sc-space-sm);
      }

      :host([compact]) .tile-temp {
        font-size: var(--sc-font-xl);
      }

      :host([compact]) .tile-stats {
        display: none;
      }

      :host([compact]) .tile-schedule {
        display: none;
      }
    `],e([mt({attribute:!1})],Nt.prototype,"hass",void 0),e([mt({type:String})],Nt.prototype,"roomSlug",void 0),e([mt({type:Boolean})],Nt.prototype,"compact",void 0),Nt=e([ht("room-tile")],Nt);let Mt=class extends dt{_getComfort(){return xt(this.hass,"sensor.sc_house_comfort")}_getEfficiency(){return xt(this.hass,"sensor.sc_house_efficiency")}_getSchedule(){return xt(this.hass,"sensor.sc_active_schedule")}_getHvacStatus(){return xt(this.hass,"sensor.sc_hvac_status")}_getFollowMe(){return xt(this.hass,"binary_sensor.sc_follow_me_active")}_renderSegmentedBar(t){const e=Math.round(t/100*10),s=kt(t);return q`
      <div class="progress-segmented">
        ${Array.from({length:10}).map((t,a)=>q`
            <div
              class="progress-segment"
              style="background: ${a<e?s:"rgba(255,255,255,0.06)"}"
            ></div>
          `)}
      </div>
    `}render(){const t=this._getComfort(),e=this._getEfficiency(),s=this._getSchedule(),a=this._getHvacStatus(),i=this._getFollowMe(),r=t?parseFloat(t.state):NaN,o=e?parseFloat(e.state):NaN,n=a?.state||"idle",c="on"===i?.state,l=i?.attributes?.target_room||"",d=s?.state||"None";return q`
      <div class="overview">
        <!-- Title -->
        <div class="overview-header">
          <div>
            <div class="overview-title">Smart Climate</div>
            <div class="overview-subtitle">Whole-house overview</div>
          </div>
        </div>

        <!-- Score blocks -->
        <div class="overview-scores">
          <div class="score-block">
            <div class="score-label">Comfort</div>
            <div
              class="score-value"
              style="color: ${kt(r)}"
            >
              ${wt(r)}
            </div>
            <div class="score-sublabel">${St(r)}</div>
            ${isNaN(r)?Y:this._renderSegmentedBar(r)}
          </div>

          <div class="score-block">
            <div class="score-label">Efficiency</div>
            <div
              class="score-value"
              style="color: ${kt(o)}"
            >
              ${wt(o)}
            </div>
            <div class="score-sublabel">
              ${isNaN(o)?"--":`${Math.round(o)}%`}
            </div>
            ${isNaN(o)?Y:this._renderSegmentedBar(o)}
          </div>
        </div>

        <!-- Status chips -->
        <div class="overview-status">
          <!-- HVAC Status -->
          <div class="status-chip">
            <div
              class="status-dot ${"idle"!==n&&"off"!==n?"sc-dot-pulse":""}"
              style="background: ${Et(n)}"
            ></div>
            <span>${Ct(n)}</span>
            <span class="status-label"
              >HVAC: ${n.charAt(0).toUpperCase()+n.slice(1)}</span
            >
          </div>

          <!-- Follow-Me -->
          ${c?q`
                <div class="status-chip">
                  <div
                    class="status-dot sc-dot-pulse"
                    style="background: var(--sc-comfort-good)"
                  ></div>
                  <span class="status-label">Follow-Me: ${l}</span>
                </div>
              `:Y}

          <!-- Active Schedule -->
          <div class="status-chip">
            <span class="status-label">Schedule: ${d}</span>
          </div>
        </div>
      </div>
    `}};Mt.styles=[ft,bt,n`
      :host {
        display: block;
      }

      .overview {
        display: flex;
        flex-direction: column;
        gap: var(--sc-space-md);
        padding-bottom: var(--sc-space-md);
      }

      /* Title row */
      .overview-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
      }

      .overview-title {
        font-size: var(--sc-font-lg);
        font-weight: 700;
        color: var(--sc-text-primary);
        letter-spacing: -0.3px;
      }

      .overview-subtitle {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
        margin-top: 2px;
      }

      /* Scores row */
      .overview-scores {
        display: flex;
        gap: var(--sc-space-md);
        flex-wrap: wrap;
      }

      .score-block {
        flex: 1;
        min-width: 100px;
        background: var(--sc-tile-bg);
        border: 1px solid var(--sc-tile-border);
        border-radius: var(--sc-radius-md);
        padding: var(--sc-space-sm) var(--sc-space-md);
      }

      .score-label {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: var(--sc-space-xs);
      }

      .score-value {
        font-size: var(--sc-font-xl);
        font-weight: 700;
        line-height: 1;
      }

      .score-sublabel {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-secondary);
        margin-top: 2px;
      }

      /* Segmented progress bar */
      .progress-segmented {
        display: flex;
        gap: 2px;
        height: 4px;
        margin-top: var(--sc-space-sm);
      }

      .progress-segment {
        flex: 1;
        border-radius: 2px;
        transition: background-color 0.3s ease;
      }

      /* Status row */
      .overview-status {
        display: flex;
        flex-wrap: wrap;
        gap: var(--sc-space-sm);
      }

      .status-chip {
        display: inline-flex;
        align-items: center;
        gap: var(--sc-space-xs);
        padding: var(--sc-space-xs) var(--sc-space-sm);
        background: var(--sc-tile-bg);
        border: 1px solid var(--sc-tile-border);
        border-radius: var(--sc-radius-xl);
        font-size: var(--sc-font-xs);
        color: var(--sc-text-secondary);
        white-space: nowrap;
      }

      .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        flex-shrink: 0;
      }

      .status-label {
        font-weight: 500;
      }
    `],e([mt({attribute:!1})],Mt.prototype,"hass",void 0),Mt=e([ht("house-overview")],Mt);const Pt=n`
  :host {
    display: block;
    font-family: var(--ha-card-font-family, 'Roboto', 'Noto', sans-serif);
    color: var(--sc-text-primary);
  }

  /* Main card container - glassmorphism */
  .sc-card {
    background: var(--sc-card-bg);
    backdrop-filter: var(--sc-backdrop-blur);
    -webkit-backdrop-filter: var(--sc-backdrop-blur);
    border: 1px solid var(--sc-card-border);
    border-radius: var(--sc-radius-xl);
    box-shadow: var(--sc-card-shadow);
    padding: var(--sc-space-lg);
    overflow: hidden;
  }

  /* Room grid layout - responsive columns */
  .sc-room-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--sc-space-md);
    padding: var(--sc-space-sm) 0;
  }

  @media (min-width: 800px) {
    .sc-room-grid {
      grid-template-columns: repeat(3, 1fr);
    }
  }

  @media (max-width: 500px) {
    .sc-room-grid {
      grid-template-columns: 1fr;
    }
  }

  /* Compact mode: smaller tiles */
  .sc-room-grid.compact {
    gap: var(--sc-space-sm);
  }

  /* Section headers */
  .sc-section {
    margin-top: var(--sc-space-lg);
    border-top: 1px solid var(--sc-section-border);
    padding-top: var(--sc-space-md);
  }

  .sc-section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    padding: var(--sc-space-sm) 0;
    user-select: none;
    -webkit-user-select: none;
  }

  .sc-section-header:hover {
    opacity: 0.8;
  }

  .sc-section-title {
    font-size: var(--sc-font-md);
    font-weight: 600;
    color: var(--sc-text-primary);
    display: flex;
    align-items: center;
    gap: var(--sc-space-sm);
  }

  .sc-section-badge {
    background: var(--sc-tile-bg);
    border-radius: var(--sc-radius-sm);
    padding: 2px 8px;
    font-size: var(--sc-font-xs);
    font-weight: 500;
    color: var(--sc-text-secondary);
  }

  .sc-section-chevron {
    font-size: var(--sc-font-md);
    color: var(--sc-text-muted);
    transition: transform 0.3s ease;
  }

  .sc-section-chevron.open {
    transform: rotate(180deg);
  }

  .sc-section-content {
    overflow: hidden;
    max-height: 0;
    opacity: 0;
    transition: max-height 0.4s ease, opacity 0.3s ease;
  }

  .sc-section-content.open {
    max-height: 2000px;
    opacity: 1;
  }

  /* Buttons */
  .sc-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--sc-space-xs);
    padding: var(--sc-space-sm) var(--sc-space-md);
    border: 1px solid var(--sc-tile-border);
    border-radius: var(--sc-radius-sm);
    background: var(--sc-tile-bg);
    color: var(--sc-text-primary);
    font-size: var(--sc-font-sm);
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s ease, border-color 0.2s ease;
    user-select: none;
    -webkit-user-select: none;
    outline: none;
  }

  .sc-btn:hover {
    background: var(--sc-tile-bg-hover);
  }

  .sc-btn:active {
    transform: scale(0.97);
  }

  .sc-btn.primary {
    background: rgba(33, 150, 243, 0.2);
    border-color: rgba(33, 150, 243, 0.4);
    color: #64b5f6;
  }

  .sc-btn.primary:hover {
    background: rgba(33, 150, 243, 0.3);
  }

  .sc-btn.success {
    background: rgba(76, 175, 80, 0.2);
    border-color: rgba(76, 175, 80, 0.4);
    color: #81c784;
  }

  .sc-btn.success:hover {
    background: rgba(76, 175, 80, 0.3);
  }

  .sc-btn.danger {
    background: rgba(244, 67, 54, 0.2);
    border-color: rgba(244, 67, 54, 0.4);
    color: #e57373;
  }

  .sc-btn.danger:hover {
    background: rgba(244, 67, 54, 0.3);
  }

  .sc-btn.small {
    padding: var(--sc-space-xs) var(--sc-space-sm);
    font-size: var(--sc-font-xs);
  }

  /* Progress bar base */
  .sc-progress {
    width: 100%;
    height: 6px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 3px;
    overflow: hidden;
  }

  .sc-progress-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.6s ease, background-color 0.3s ease;
  }

  /* No data / empty state */
  .sc-empty {
    text-align: center;
    padding: var(--sc-space-xl);
    color: var(--sc-text-muted);
    font-size: var(--sc-font-md);
  }

  /* Overlay / drawer backdrop */
  .sc-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    z-index: 999;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  /* Loading dots */
  .sc-loading {
    display: flex;
    gap: var(--sc-space-xs);
    justify-content: center;
    padding: var(--sc-space-lg);
  }

  .sc-loading-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--sc-text-muted);
    animation: sc-loading-bounce 1.4s infinite ease-in-out both;
  }

  .sc-loading-dot:nth-child(1) { animation-delay: -0.32s; }
  .sc-loading-dot:nth-child(2) { animation-delay: -0.16s; }

  @keyframes sc-loading-bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
  }
`;let Tt=class extends dt{constructor(){super(...arguments),this._expanded=!1,this._loading=new Set}_getSuggestionCount(){const t=xt(this.hass,"sensor.sc_ai_suggestion_count");if(!t)return 0;const e=parseInt(t.state,10);return isNaN(e)?0:e}_getSuggestions(){const t=xt(this.hass,"sensor.sc_ai_suggestion_count");if(!t)return[];const e=t.attributes?.pending_titles||[],s=t.attributes?.pending_ids||[],a=xt(this.hass,"sensor.sc_ai_daily_summary"),i=a?.attributes?.suggestions||[];return i.length>0?i:e.map((t,e)=>({id:s[e]||`suggestion_${e}`,title:t,description:"",confidence:3,priority:"medium",category:"general"}))}_getDailySummary(){const t=xt(this.hass,"sensor.sc_ai_daily_summary");return t?.state||""}_getLastAnalysis(){const t=xt(this.hass,"sensor.sc_ai_last_analysis");return t&&"unknown"!==t.state&&"unavailable"!==t.state?t.state:""}_toggleExpand(){this._expanded=!this._expanded}async _approve(t){this._loading=new Set([...this._loading,t]),this.requestUpdate();try{await yt(this.hass,"smart_climate","approve_suggestion",{suggestion_id:t})}catch(t){console.error("Failed to approve suggestion:",t)}this._loading.delete(t),this._loading=new Set(this._loading),this.requestUpdate()}async _reject(t){this._loading=new Set([...this._loading,t]),this.requestUpdate();try{await yt(this.hass,"smart_climate","reject_suggestion",{suggestion_id:t})}catch(t){console.error("Failed to reject suggestion:",t)}this._loading.delete(t),this._loading=new Set(this._loading),this.requestUpdate()}async _approveAll(){const t=this._getSuggestions();for(const e of t)await this._approve(e.id)}async _rejectAll(){const t=this._getSuggestions();for(const e of t)await this._reject(e.id)}render(){const t=this._getSuggestionCount(),e=this._getSuggestions(),s=this._getDailySummary(),a=this._getLastAnalysis();return q`
      <div class="sc-section">
        <!-- Collapsible header -->
        <div class="sc-section-header" @click=${this._toggleExpand}>
          <div class="sc-section-title">
            AI Suggestions
            ${t>0?q`<span class="sc-section-badge">${t}</span>`:Y}
          </div>
          <span class="sc-section-chevron ${this._expanded?"open":""}"
            >&#9662;</span
          >
        </div>

        <!-- Collapsible content -->
        <div class="sc-section-content ${this._expanded?"open":""}">
          <!-- Daily summary -->
          ${s&&"unknown"!==s&&"unavailable"!==s?q`
                <div class="daily-summary">
                  <div class="daily-summary-label">Daily Summary</div>
                  ${s}
                </div>
              `:Y}

          <!-- Suggestion cards -->
          ${e.length>0?q`
                <div class="suggestion-list">
                  ${e.map(t=>q`
                      <div
                        class="suggestion-card sc-fade-in ${this._loading.has(t.id)?"loading":""}"
                      >
                        <div class="suggestion-header">
                          <span class="suggestion-title">${t.title}</span>
                          <span
                            class="suggestion-priority ${t.priority.toLowerCase()}"
                            >${t.priority}</span
                          >
                        </div>

                        ${t.description?q`<div class="suggestion-desc">
                              ${t.description}
                            </div>`:Y}

                        <div class="suggestion-meta">
                          <span class="suggestion-confidence">
                            Confidence:
                            <span class="confidence-dots"
                              >${function(t){const e=Math.min(Math.max(Math.round(t),0),5),s=5-e;return"●".repeat(e)+"○".repeat(s)}(t.confidence)}</span
                            >
                          </span>
                          ${t.category?q`<span class="suggestion-category"
                                >${t.category}</span
                              >`:Y}
                        </div>

                        <div class="suggestion-actions">
                          <button
                            class="sc-btn danger small"
                            @click=${e=>{e.stopPropagation(),this._reject(t.id)}}
                          >
                            Reject
                          </button>
                          <button
                            class="sc-btn success small"
                            @click=${e=>{e.stopPropagation(),this._approve(t.id)}}
                          >
                            Approve
                          </button>
                        </div>
                      </div>
                    `)}
                </div>

                <!-- Bulk actions -->
                ${e.length>1?q`
                      <div class="bulk-actions">
                        <button
                          class="sc-btn danger small"
                          @click=${this._rejectAll}
                        >
                          Reject All
                        </button>
                        <button
                          class="sc-btn success small"
                          @click=${this._approveAll}
                        >
                          Approve All
                        </button>
                      </div>
                    `:Y}
              `:q`
                <div class="sc-empty">No pending suggestions</div>
              `}

          <!-- Last analysis time -->
          ${a?q`<div class="last-analysis">
                Last analysis: ${a}
              </div>`:Y}
        </div>
      </div>
    `}};Tt.styles=[ft,bt,Pt,n`
      :host {
        display: block;
      }

      .suggestion-list {
        display: flex;
        flex-direction: column;
        gap: var(--sc-space-sm);
        padding: var(--sc-space-sm) 0;
      }

      .suggestion-card {
        background: var(--sc-tile-bg);
        border: 1px solid var(--sc-tile-border);
        border-radius: var(--sc-radius-md);
        padding: var(--sc-space-md);
        transition: background 0.2s ease;
      }

      .suggestion-card:hover {
        background: var(--sc-tile-bg-hover);
      }

      .suggestion-card.loading {
        opacity: 0.5;
        pointer-events: none;
      }

      /* Card header */
      .suggestion-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: var(--sc-space-sm);
        margin-bottom: var(--sc-space-sm);
      }

      .suggestion-title {
        font-size: var(--sc-font-md);
        font-weight: 600;
        color: var(--sc-text-primary);
        flex: 1;
      }

      .suggestion-priority {
        font-size: var(--sc-font-xs);
        font-weight: 600;
        padding: 2px 8px;
        border-radius: var(--sc-radius-sm);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        flex-shrink: 0;
      }

      .suggestion-priority.high {
        background: rgba(244, 67, 54, 0.15);
        color: var(--sc-priority-high);
        border: 1px solid rgba(244, 67, 54, 0.3);
      }

      .suggestion-priority.medium {
        background: rgba(255, 152, 0, 0.15);
        color: var(--sc-priority-medium);
        border: 1px solid rgba(255, 152, 0, 0.3);
      }

      .suggestion-priority.low {
        background: rgba(76, 175, 80, 0.15);
        color: var(--sc-priority-low);
        border: 1px solid rgba(76, 175, 80, 0.3);
      }

      /* Description */
      .suggestion-desc {
        font-size: var(--sc-font-sm);
        color: var(--sc-text-secondary);
        line-height: 1.5;
        margin-bottom: var(--sc-space-sm);
      }

      /* Confidence row */
      .suggestion-meta {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: var(--sc-space-sm);
      }

      .suggestion-confidence {
        font-size: var(--sc-font-sm);
        color: var(--sc-text-muted);
        display: flex;
        align-items: center;
        gap: var(--sc-space-xs);
      }

      .confidence-dots {
        letter-spacing: 1px;
        color: var(--sc-comfort-fair);
      }

      .suggestion-category {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
        background: rgba(255, 255, 255, 0.04);
        padding: 2px 6px;
        border-radius: 4px;
      }

      /* Action buttons */
      .suggestion-actions {
        display: flex;
        gap: var(--sc-space-sm);
        justify-content: flex-end;
      }

      /* Bulk actions */
      .bulk-actions {
        display: flex;
        justify-content: flex-end;
        gap: var(--sc-space-sm);
        padding-top: var(--sc-space-sm);
        border-top: 1px solid var(--sc-section-border);
        margin-top: var(--sc-space-sm);
      }

      /* Daily summary */
      .daily-summary {
        font-size: var(--sc-font-sm);
        color: var(--sc-text-secondary);
        line-height: 1.5;
        padding: var(--sc-space-sm);
        background: var(--sc-tile-bg);
        border-radius: var(--sc-radius-sm);
        margin-bottom: var(--sc-space-sm);
        border-left: 3px solid var(--sc-comfort-good);
      }

      .daily-summary-label {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: var(--sc-space-xs);
      }

      .last-analysis {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
        text-align: right;
        margin-top: var(--sc-space-sm);
      }
    `],e([mt({attribute:!1})],Tt.prototype,"hass",void 0),e([gt()],Tt.prototype,"_expanded",void 0),e([gt()],Tt.prototype,"_loading",void 0),Tt=e([ht("suggestion-panel")],Tt);let Ot=class extends dt{constructor(){super(...arguments),this._expanded=!1,this._colors=["#4caf50","#2196f3","#ff9800","#9c27b0","#00bcd4","#e91e63","#8bc34a","#ff5722"]}_getScheduleBlocks(){const t=xt(this.hass,"sensor.sc_active_schedule");if(!t)return[];const e=t.attributes?.today_blocks||[],s=new Map;let a=0;return e.map(t=>t.color?t:(s.has(t.name)||(s.set(t.name,this._colors[a%this._colors.length]),a++),{...t,color:s.get(t.name)||"#9e9e9e"}))}_toggleExpand(){this._expanded=!this._expanded}_timeToPercent(t,e){return(60*t+e)/1440*100}_renderTimeline(t){const e=new Date,s=this._timeToPercent(e.getHours(),e.getMinutes()),a=15;return W`
      <svg
        class="timeline-svg"
        viewBox="0 0 ${100} ${55}"
        preserveAspectRatio="none"
      >
        <!-- Background track -->
        <rect
          x="0" y="${a}"
          width="${100}" height="${20}"
          rx="4" ry="4"
          fill="rgba(255,255,255,0.04)"
        />

        <!-- Hour markers -->
        ${[6,12,18].map(t=>W`
            <line
              x1="${this._timeToPercent(t,0)}" y1="${a}"
              x2="${this._timeToPercent(t,0)}" y2="${35}"
              stroke="rgba(255,255,255,0.08)"
              stroke-width="0.3"
            />
            <text
              x="${this._timeToPercent(t,0)}"
              y="${45}"
              text-anchor="middle"
              fill="rgba(255,255,255,0.3)"
              font-size="3.5"
              font-family="sans-serif"
            >
              ${12===t?"12p":t<12?`${t}a`:t-12+"p"}
            </text>
          `)}

        <!-- Schedule blocks -->
        ${t.map(t=>{const e=this._timeToPercent(t.start_hour,t.start_minute),s=this._timeToPercent(t.end_hour,t.end_minute),a=Math.max(.5,s-e);return W`
            <rect
              x="${e}" y="${16}"
              width="${a}" height="${18}"
              rx="2" ry="2"
              fill="${t.color}"
              opacity="0.7"
            >
              <title>${t.name}: ${t.start_hour}:${String(t.start_minute).padStart(2,"0")} - ${t.end_hour}:${String(t.end_minute).padStart(2,"0")}</title>
            </rect>
          `})}

        <!-- NOW marker -->
        <line
          x1="${s}" y1="${11}"
          x2="${s}" y2="${39}"
          stroke="#ff5252"
          stroke-width="0.6"
        />
        <circle
          cx="${s}" cy="${11}"
          r="2"
          fill="#ff5252"
        />
        <text
          x="${s}"
          y="${8}"
          text-anchor="middle"
          fill="#ff5252"
          font-size="3"
          font-weight="bold"
          font-family="sans-serif"
        >
          NOW
        </text>
      </svg>
    `}render(){const t=this._getScheduleBlocks(),e=xt(this.hass,"sensor.sc_active_schedule"),s=e?.state||"None",a=new Date,i=new Map;return t.forEach(t=>i.set(t.name,t.color)),q`
      <div class="sc-section">
        <!-- Collapsible header -->
        <div class="sc-section-header" @click=${this._toggleExpand}>
          <div class="sc-section-title">
            Schedule
            <span class="sc-section-badge">${s}</span>
          </div>
          <span class="sc-section-chevron ${this._expanded?"open":""}"
            >&#9662;</span
          >
        </div>

        <!-- Collapsible content -->
        <div class="sc-section-content ${this._expanded?"open":""}">
          <div class="active-schedule-info">
            Active:
            <span class="active-schedule-name">${s}</span>
            &middot; ${r=a,r.toLocaleTimeString("en-US",{hour:"numeric",minute:"2-digit",hour12:!0})}
          </div>

          ${t.length>0?q`
                <div class="timeline-container">
                  ${this._renderTimeline(t)}
                  <div class="timeline-labels">
                    <span>12 AM</span>
                    <span>6 AM</span>
                    <span>12 PM</span>
                    <span>6 PM</span>
                    <span>12 AM</span>
                  </div>
                </div>

                <!-- Legend -->
                <div class="schedule-legend">
                  ${[...i.entries()].map(([t,e])=>q`
                      <div class="legend-item">
                        <span
                          class="legend-dot"
                          style="background: ${e}"
                        ></span>
                        ${t}
                      </div>
                    `)}
                </div>
              `:q`<div class="sc-empty">No schedules configured for today</div>`}
        </div>
      </div>
    `;var r}};Ot.styles=[ft,bt,Pt,n`
      :host {
        display: block;
      }

      .timeline-container {
        padding: var(--sc-space-sm) 0;
      }

      .timeline-svg {
        width: 100%;
        height: 60px;
        display: block;
      }

      .timeline-labels {
        display: flex;
        justify-content: space-between;
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
        margin-top: var(--sc-space-xs);
        padding: 0 2px;
      }

      .schedule-legend {
        display: flex;
        flex-wrap: wrap;
        gap: var(--sc-space-sm);
        margin-top: var(--sc-space-sm);
        padding: var(--sc-space-xs) 0;
      }

      .legend-item {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: var(--sc-font-xs);
        color: var(--sc-text-secondary);
      }

      .legend-dot {
        width: 8px;
        height: 8px;
        border-radius: 2px;
        flex-shrink: 0;
      }

      .active-schedule-info {
        font-size: var(--sc-font-sm);
        color: var(--sc-text-secondary);
        margin-bottom: var(--sc-space-sm);
      }

      .active-schedule-name {
        color: var(--sc-text-primary);
        font-weight: 600;
      }
    `],e([mt({attribute:!1})],Ot.prototype,"hass",void 0),e([gt()],Ot.prototype,"_expanded",void 0),Ot=e([ht("schedule-view")],Ot);let Ht=class extends dt{constructor(){super(...arguments),this.roomSlug="",this.open=!1,this._targetTemp=72,this._hvacMode="auto"}_entity(t){return xt(this.hass,`sensor.sc_${this.roomSlug}_${t}`)}_binaryEntity(t){return xt(this.hass,`binary_sensor.sc_${this.roomSlug}_${t}`)}_close(){this.dispatchEvent(new CustomEvent("room-detail-close",{bubbles:!0,composed:!0}))}_handleOverlayClick(t){t.target.classList.contains("detail-overlay")&&this._close()}_adjustTarget(t){this._targetTemp=Math.round(2*(this._targetTemp+t))/2,yt(this.hass,"smart_climate","set_target_temperature",{room:this.roomSlug,temperature:this._targetTemp}).catch(t=>console.error("Failed to set target temperature:",t))}_setMode(t){this._hvacMode=t,yt(this.hass,"smart_climate","set_hvac_mode",{room:this.roomSlug,mode:t}).catch(t=>console.error("Failed to set HVAC mode:",t))}updated(t){if(t.has("roomSlug")||t.has("open")){const t=this._entity("target_temperature");if(t){const e=parseFloat(t.state);isNaN(e)||(this._targetTemp=e)}const e=this._entity("hvac_mode");e&&"unknown"!==e.state&&(this._hvacMode=e.state)}}render(){if(!this.open||!this.roomSlug)return Y;const t=this._entity("comfort_score"),e=this._entity("efficiency"),s=this._entity("temperature"),a=this._entity("humidity"),i=this._entity("temperature_trend"),r=this._entity("hvac_action"),o=this._entity("hvac_runtime"),n=this._entity("active_schedule"),c=this._entity("vent_position"),l=this._entity("auxiliary"),d=t?parseFloat(t.state):NaN,p=e?parseFloat(e.state):NaN,h=s?.state,u=a?.state,v=i?.state,m=r?.state||"idle",g=o?.state,f=n?.state||"None",b=s?.attributes?.unit_of_measurement||"°F",y=c?.state,x=c?.attributes?.friendly_name||"Vent",_=l?.attributes?.devices||[],$=t?.attributes?.sensors||[];return q`
      <div class="detail-overlay" @click=${this._handleOverlayClick}>
        <div class="detail-drawer">
          <!-- Handle -->
          <div class="detail-handle"></div>

          <!-- Header -->
          <div class="detail-header">
            <span class="detail-title">${_t(this.roomSlug)}</span>
            <button class="detail-close" @click=${this._close}>&times;</button>
          </div>

          <!-- Temperature display -->
          <div class="detail-section">
            <div class="detail-temp-display">
              <span class="detail-temp-value">${$t(h,"")}</span>
              <span class="detail-temp-unit">${b}</span>
              <span class="detail-temp-trend">${At(v)}</span>
            </div>
          </div>

          <!-- Stats grid -->
          <div class="detail-section">
            <div class="detail-stats">
              <div class="detail-stat">
                <div class="detail-stat-label">Humidity</div>
                <div class="detail-stat-value">
                  ${u&&"unknown"!==u?`${Math.round(parseFloat(u))}%`:"--"}
                </div>
              </div>
              <div class="detail-stat">
                <div class="detail-stat-label">HVAC</div>
                <div class="detail-stat-value" style="color: ${Et(m)}">
                  ${Ct(m)}
                  ${m.charAt(0).toUpperCase()+m.slice(1)}
                </div>
                <div class="detail-stat-sub">Runtime: ${zt(g)}</div>
              </div>
              <div class="detail-stat">
                <div class="detail-stat-label">Schedule</div>
                <div class="detail-stat-value">${f}</div>
              </div>
              <div class="detail-stat">
                <div class="detail-stat-label">Target</div>
                <div class="detail-stat-value">${$t(this._targetTemp,b)}</div>
              </div>
            </div>
          </div>

          <!-- Comfort / Efficiency bars -->
          <div class="detail-section">
            <div class="detail-section-title">Performance</div>

            <div class="detail-bar-row">
              <span class="detail-bar-label">Comfort</span>
              <div class="detail-bar">
                <div
                  class="detail-bar-fill"
                  style="width: ${isNaN(d)?0:d}%; background: ${kt(d)}"
                ></div>
              </div>
              <span class="detail-bar-value" style="color: ${kt(d)}">
                ${wt(d)}
              </span>
            </div>

            <div class="detail-bar-row">
              <span class="detail-bar-label">Efficiency</span>
              <div class="detail-bar">
                <div
                  class="detail-bar-fill"
                  style="width: ${isNaN(p)?0:p}%; background: ${kt(p)}"
                ></div>
              </div>
              <span class="detail-bar-value" style="color: ${kt(p)}">
                ${wt(p)}
              </span>
            </div>

            <!-- Efficiency chart -->
            <efficiency-chart
              .hass=${this.hass}
              .roomSlug=${this.roomSlug}
            ></efficiency-chart>
          </div>

          <!-- Climate controls -->
          <div class="detail-section">
            <div class="detail-section-title">Climate Control</div>
            <div class="detail-controls">
              <!-- Target temperature -->
              <div class="control-row">
                <span class="control-label">Target</span>
                <div class="temp-control">
                  <button class="temp-btn" @click=${()=>this._adjustTarget(-.5)}>-</button>
                  <span class="temp-display">${$t(this._targetTemp,b)}</span>
                  <button class="temp-btn" @click=${()=>this._adjustTarget(.5)}>+</button>
                </div>
              </div>

              <!-- Mode select -->
              <div class="control-row">
                <span class="control-label">Mode</span>
                <div class="mode-select">
                  ${["auto","heat","cool","fan_only","off"].map(t=>q`
                      <button
                        class="mode-btn ${this._hvacMode===t?"active":""}"
                        @click=${()=>this._setMode(t)}
                      >
                        ${t.replace("_"," ")}
                      </button>
                    `)}
                </div>
              </div>
            </div>
          </div>

          <!-- Vent status -->
          ${y&&"unknown"!==y&&"unavailable"!==y?q`
                <div class="detail-section">
                  <div class="detail-section-title">Vent</div>
                  <div class="vent-status">
                    <span class="vent-icon">🔲</span>
                    <div class="vent-info">
                      <div class="vent-name">${x}</div>
                      <div class="vent-position">Position: ${y}%</div>
                    </div>
                  </div>
                </div>
              `:Y}

          <!-- Auxiliary devices -->
          ${_.length>0?q`
                <div class="detail-section">
                  <div class="detail-section-title">Auxiliary Devices</div>
                  <div class="device-list">
                    ${_.map(t=>q`
                        <div class="device-item">
                          <span class="device-icon">
                            ${"on"===t.state||"active"===t.state?"🟢":"⚫"}
                          </span>
                          <span class="device-name">${t.name}</span>
                          <span class="device-state">${t.state}</span>
                        </div>
                      `)}
                  </div>
                </div>
              `:Y}

          <!-- Sensor list -->
          ${$.length>0?q`
                <div class="detail-section">
                  <div class="detail-section-title">Sensors</div>
                  <div class="device-list">
                    ${$.map(t=>q`
                        <div class="device-item">
                          <span class="device-icon">📡</span>
                          <span class="device-name">${t.name}</span>
                          <span class="device-state">${t.state}</span>
                        </div>
                      `)}
                  </div>
                </div>
              `:Y}
        </div>
      </div>
    `}};Ht.styles=[ft,bt,Pt,n`
      :host {
        display: block;
      }

      /* Overlay backdrop */
      .detail-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        z-index: 1000;
        display: flex;
        align-items: flex-end;
        justify-content: center;
      }

      /* Drawer panel */
      .detail-drawer {
        width: 100%;
        max-width: 500px;
        max-height: 90vh;
        background: var(--sc-card-bg-solid);
        border-radius: var(--sc-radius-xl) var(--sc-radius-xl) 0 0;
        overflow-y: auto;
        padding: var(--sc-space-lg);
        animation: sc-slide-up 0.35s cubic-bezier(0.4, 0, 0.2, 1) forwards;
      }

      /* Close handle */
      .detail-handle {
        width: 40px;
        height: 4px;
        background: var(--sc-text-muted);
        border-radius: 2px;
        margin: 0 auto var(--sc-space-lg);
      }

      /* Header */
      .detail-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: var(--sc-space-lg);
      }

      .detail-title {
        font-size: var(--sc-font-xl);
        font-weight: 700;
        color: var(--sc-text-primary);
      }

      .detail-close {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: var(--sc-tile-bg);
        border: 1px solid var(--sc-tile-border);
        color: var(--sc-text-secondary);
        font-size: var(--sc-font-lg);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.2s;
      }

      .detail-close:hover {
        background: var(--sc-tile-bg-hover);
      }

      /* Sections */
      .detail-section {
        margin-bottom: var(--sc-space-lg);
      }

      .detail-section-title {
        font-size: var(--sc-font-sm);
        font-weight: 600;
        color: var(--sc-text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: var(--sc-space-sm);
      }

      /* Big temp display */
      .detail-temp-display {
        display: flex;
        align-items: baseline;
        gap: var(--sc-space-sm);
        margin-bottom: var(--sc-space-md);
      }

      .detail-temp-value {
        font-size: 3rem;
        font-weight: 700;
        line-height: 1;
        color: var(--sc-text-primary);
      }

      .detail-temp-unit {
        font-size: var(--sc-font-lg);
        color: var(--sc-text-muted);
      }

      .detail-temp-trend {
        font-size: var(--sc-font-xl);
        color: var(--sc-text-secondary);
      }

      /* Stats grid */
      .detail-stats {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: var(--sc-space-sm);
      }

      .detail-stat {
        background: var(--sc-tile-bg);
        border: 1px solid var(--sc-tile-border);
        border-radius: var(--sc-radius-md);
        padding: var(--sc-space-sm) var(--sc-space-md);
      }

      .detail-stat-label {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
        margin-bottom: 2px;
      }

      .detail-stat-value {
        font-size: var(--sc-font-lg);
        font-weight: 600;
        color: var(--sc-text-primary);
      }

      .detail-stat-sub {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-secondary);
      }

      /* Comfort/efficiency bars */
      .detail-bar-row {
        display: flex;
        align-items: center;
        gap: var(--sc-space-sm);
        margin-bottom: var(--sc-space-sm);
      }

      .detail-bar-label {
        font-size: var(--sc-font-sm);
        color: var(--sc-text-secondary);
        min-width: 80px;
      }

      .detail-bar {
        flex: 1;
        height: 8px;
        background: rgba(255, 255, 255, 0.06);
        border-radius: 4px;
        overflow: hidden;
      }

      .detail-bar-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.6s ease;
      }

      .detail-bar-value {
        font-size: var(--sc-font-sm);
        font-weight: 600;
        min-width: 40px;
        text-align: right;
      }

      /* Climate controls */
      .detail-controls {
        display: flex;
        flex-direction: column;
        gap: var(--sc-space-md);
      }

      .control-row {
        display: flex;
        align-items: center;
        gap: var(--sc-space-md);
      }

      .control-label {
        font-size: var(--sc-font-sm);
        color: var(--sc-text-secondary);
        min-width: 80px;
      }

      .temp-control {
        display: flex;
        align-items: center;
        gap: var(--sc-space-sm);
      }

      .temp-btn {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: var(--sc-tile-bg);
        border: 1px solid var(--sc-tile-border);
        color: var(--sc-text-primary);
        font-size: var(--sc-font-lg);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.2s;
        user-select: none;
      }

      .temp-btn:hover {
        background: var(--sc-tile-bg-hover);
      }

      .temp-btn:active {
        transform: scale(0.93);
      }

      .temp-display {
        font-size: var(--sc-font-xl);
        font-weight: 600;
        color: var(--sc-text-primary);
        min-width: 60px;
        text-align: center;
      }

      /* Mode select */
      .mode-select {
        display: flex;
        gap: var(--sc-space-xs);
      }

      .mode-btn {
        padding: var(--sc-space-xs) var(--sc-space-md);
        border-radius: var(--sc-radius-sm);
        background: var(--sc-tile-bg);
        border: 1px solid var(--sc-tile-border);
        color: var(--sc-text-secondary);
        font-size: var(--sc-font-xs);
        cursor: pointer;
        transition: background 0.2s, color 0.2s;
      }

      .mode-btn:hover {
        background: var(--sc-tile-bg-hover);
      }

      .mode-btn.active {
        background: rgba(33, 150, 243, 0.2);
        border-color: rgba(33, 150, 243, 0.4);
        color: #64b5f6;
      }

      /* Device list */
      .device-list {
        display: flex;
        flex-direction: column;
        gap: var(--sc-space-xs);
      }

      .device-item {
        display: flex;
        align-items: center;
        gap: var(--sc-space-sm);
        padding: var(--sc-space-sm);
        background: var(--sc-tile-bg);
        border-radius: var(--sc-radius-sm);
        font-size: var(--sc-font-sm);
        color: var(--sc-text-secondary);
      }

      .device-icon {
        font-size: var(--sc-font-md);
      }

      .device-name {
        flex: 1;
        color: var(--sc-text-primary);
      }

      .device-state {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
      }

      /* Vent status */
      .vent-status {
        display: flex;
        align-items: center;
        gap: var(--sc-space-sm);
        padding: var(--sc-space-sm);
        background: var(--sc-tile-bg);
        border-radius: var(--sc-radius-sm);
      }

      .vent-icon {
        font-size: var(--sc-font-lg);
      }

      .vent-info {
        flex: 1;
      }

      .vent-name {
        font-size: var(--sc-font-sm);
        color: var(--sc-text-primary);
      }

      .vent-position {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
      }
    `],e([mt({attribute:!1})],Ht.prototype,"hass",void 0),e([mt({type:String})],Ht.prototype,"roomSlug",void 0),e([mt({type:Boolean})],Ht.prototype,"open",void 0),e([gt()],Ht.prototype,"_targetTemp",void 0),e([gt()],Ht.prototype,"_hvacMode",void 0),Ht=e([ht("room-detail")],Ht);let Ut=class extends dt{constructor(){super(...arguments),this.roomSlug=""}_getEfficiencyData(){const t=xt(this.hass,this.roomSlug?`sensor.sc_${this.roomSlug}_efficiency`:"sensor.sc_house_efficiency");if(!t)return[];const e=t.attributes?.hourly_data||[];if(e.length>0)return e.slice(-12);const s=parseFloat(t.state);return isNaN(s)?[]:[s]}_renderBars(t){if(0===t.length)return Y;const e=40,s=t.map((t,s)=>{const a=Math.max(2,t/100*e),i=8.5*s,r=e-a,o=kt(t);return W`
        <rect
          x="${i}%"
          y="${r}"
          width="${6.5}%"
          height="${a}"
          rx="2"
          ry="2"
          fill="${o}"
          opacity="0.8"
        >
          <title>${Math.round(t)}%</title>
        </rect>
      `});return W`
      <svg viewBox="0 0 100 ${e}" preserveAspectRatio="none">
        <!-- Grid lines -->
        <line x1="0" y1="${10}" x2="100" y2="${10}"
              stroke="rgba(255,255,255,0.05)" stroke-width="0.5" />
        <line x1="0" y1="${20}" x2="100" y2="${20}"
              stroke="rgba(255,255,255,0.05)" stroke-width="0.5" />
        <line x1="0" y1="${30}" x2="100" y2="${30}"
              stroke="rgba(255,255,255,0.05)" stroke-width="0.5" />
        ${s}
      </svg>
    `}render(){const t=this._getEfficiencyData();return 0===t.length?Y:q`
      <div class="chart-container">
        <div class="chart-label">Efficiency</div>
        ${this._renderBars(t)}
        <div class="chart-legend">
          <span>${t.length>1?`-${t.length}h`:"Now"}</span>
          <span>Now</span>
        </div>
      </div>
    `}};Ut.styles=[ft,n`
      :host {
        display: block;
      }

      .chart-container {
        padding: var(--sc-space-sm) 0;
      }

      .chart-label {
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
        margin-bottom: var(--sc-space-xs);
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      svg {
        width: 100%;
        height: 48px;
        display: block;
      }

      .chart-legend {
        display: flex;
        justify-content: space-between;
        font-size: var(--sc-font-xs);
        color: var(--sc-text-muted);
        margin-top: 2px;
      }
    `],e([mt({attribute:!1})],Ut.prototype,"hass",void 0),e([mt({type:String})],Ut.prototype,"roomSlug",void 0),Ut=e([ht("efficiency-chart")],Ut);let Rt=class extends dt{constructor(){super(...arguments),this.roomSlug=""}_getAuxEntity(){return xt(this.hass,`sensor.sc_${this.roomSlug}_auxiliary`)}_getDeviceIcon(t){switch(t?.toLowerCase()){case"fan":case"ceiling_fan":return"🌀";case"humidifier":return"💨";case"dehumidifier":return"🌊";case"heater":case"space_heater":return"🔥";case"air_purifier":return"🌿";case"window":return"🪟";default:return"⚡"}}render(){const t=this._getAuxEntity();if(!t)return Y;const e=(t.attributes?.devices||[]).filter(t=>"on"===t.state||"active"===t.state);return 0===e.length?Y:q`
      <div class="aux-container">
        ${e.map(t=>q`
            <div class="aux-device sc-fade-in">
              <span class="aux-icon">${this._getDeviceIcon(t.type)}</span>
              <div class="aux-info">
                <div class="aux-name">${t.name}</div>
                ${t.reason?q`<div class="aux-reason">${t.reason}</div>`:Y}
              </div>
              <span class="aux-runtime">${zt(t.runtime)}</span>
              <span class="aux-status-dot on sc-dot-pulse"></span>
            </div>
          `)}
      </div>
    `}};return Rt.styles=[ft,bt,n`
      :host {
        display: block;
      }

      .aux-container {
        display: flex;
        flex-direction: column;
        gap: var(--sc-space-xs);
      }

      .aux-device {
        display: flex;
        align-items: center;
        gap: var(--sc-space-sm);
        padding: var(--sc-space-xs) var(--sc-space-sm);
        background: rgba(255, 255, 255, 0.04);
        border-radius: var(--sc-radius-sm);
        font-size: var(--sc-font-xs);
      }

      .aux-icon {
        font-size: var(--sc-font-md);
        flex-shrink: 0;
      }

      .aux-info {
        flex: 1;
        min-width: 0;
      }

      .aux-name {
        color: var(--sc-text-primary);
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .aux-detail {
        color: var(--sc-text-muted);
        font-size: var(--sc-font-xs);
      }

      .aux-status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        flex-shrink: 0;
      }

      .aux-status-dot.on {
        background: var(--sc-comfort-excellent);
      }

      .aux-status-dot.off {
        background: var(--sc-hvac-idle);
      }

      .aux-runtime {
        color: var(--sc-text-muted);
        font-size: var(--sc-font-xs);
        flex-shrink: 0;
      }

      .aux-reason {
        color: var(--sc-text-secondary);
        font-size: var(--sc-font-xs);
        font-style: italic;
        padding-left: var(--sc-space-sm);
        margin-top: 2px;
      }
    `],e([mt({attribute:!1})],Rt.prototype,"hass",void 0),e([mt({type:String})],Rt.prototype,"roomSlug",void 0),Rt=e([ht("auxiliary-status")],Rt),t.SmartClimateCard=class extends dt{constructor(){super(...arguments),this._config={},this._rooms=[],this._detailRoom="",this._detailOpen=!1}setConfig(t){this._config={show_schedule:!0,show_suggestions:!0,show_efficiency:!0,compact:!1,...t}}getCardSize(){return 6}static getStubConfig(){return{show_schedule:!0,show_suggestions:!0,show_efficiency:!0,compact:!1}}updated(t){super.updated(t),t.has("hass")&&this.hass&&this._discoverRooms()}_discoverRooms(){const t=function(t){if(!t||!t.states)return[];const e=[],s=/^sensor\.sc_(.+)_comfort_score$/;for(const a of Object.keys(t.states)){const t=a.match(s);t&&t[1]&&"house"!==t[1]&&e.push(t[1])}return e.sort()}(this.hass);if(this._config.rooms_order&&this._config.rooms_order.length>0){const e=[];for(const s of this._config.rooms_order)t.includes(s)&&e.push(s);for(const s of t)e.includes(s)||e.push(s);this._rooms=e}else this._rooms=t}_handleRoomDetailOpen(t){this._detailRoom=t.detail.roomSlug,this._detailOpen=!0}_handleRoomDetailClose(){this._detailOpen=!1,this._detailRoom=""}_getGridClasses(){const t=["sc-room-grid"];return this._config.compact&&t.push("compact"),this._config.columns&&t.push(`cols-${Math.min(3,Math.max(1,this._config.columns))}`),t.join(" ")}render(){if(!this.hass)return q`
        <ha-card>
          <div class="sc-card">
            <div class="sc-loading">
              <div class="sc-loading-dot"></div>
              <div class="sc-loading-dot"></div>
              <div class="sc-loading-dot"></div>
            </div>
          </div>
        </ha-card>
      `;const t=!1!==this._config.show_schedule,e=!1!==this._config.show_suggestions,s=this._config.compact||!1;return q`
      <ha-card>
        <div class="sc-card">
          <!-- 1. House Overview Header -->
          <house-overview .hass=${this.hass}></house-overview>

          <!-- 2. Room Grid -->
          ${this._rooms.length>0?q`
                <div class="sc-rooms-label">
                  Rooms (${this._rooms.length})
                </div>
                <div
                  class="${this._getGridClasses()}"
                  @room-detail-open=${this._handleRoomDetailOpen}
                >
                  ${this._rooms.map((t,e)=>q`
                      <room-tile
                        .hass=${this.hass}
                        .roomSlug=${t}
                        ?compact=${s}
                        class="sc-fade-in"
                        style="animation-delay: ${50*e}ms"
                      ></room-tile>
                    `)}
                </div>
              `:q`
                <div class="sc-empty">
                  No Smart Climate rooms found. Make sure the Smart Climate
                  integration is configured.
                </div>
              `}

          <!-- 3. Schedule Timeline (collapsible) -->
          ${t?q`<schedule-view .hass=${this.hass}></schedule-view>`:Y}

          <!-- 4. AI Suggestions (collapsible) -->
          ${e?q`<suggestion-panel .hass=${this.hass}></suggestion-panel>`:Y}
        </div>
      </ha-card>

      <!-- Room Detail Drawer (overlay) -->
      <room-detail
        .hass=${this.hass}
        .roomSlug=${this._detailRoom}
        ?open=${this._detailOpen}
        @room-detail-close=${this._handleRoomDetailClose}
      ></room-detail>
    `}},t.SmartClimateCard.styles=[ft,Pt,bt,n`
      :host {
        display: block;
      }

      .sc-card {
        background: var(--sc-card-bg);
        backdrop-filter: var(--sc-backdrop-blur);
        -webkit-backdrop-filter: var(--sc-backdrop-blur);
        border: 1px solid var(--sc-card-border);
        border-radius: var(--sc-radius-xl);
        box-shadow: var(--sc-card-shadow);
        padding: var(--sc-space-lg);
        overflow: hidden;
      }

      /* Grid column overrides */
      .sc-room-grid.cols-1 {
        grid-template-columns: 1fr;
      }

      .sc-room-grid.cols-2 {
        grid-template-columns: repeat(2, 1fr);
      }

      .sc-room-grid.cols-3 {
        grid-template-columns: repeat(3, 1fr);
      }

      @media (max-width: 500px) {
        .sc-room-grid.cols-2,
        .sc-room-grid.cols-3 {
          grid-template-columns: 1fr;
        }
      }

      @media (min-width: 501px) and (max-width: 800px) {
        .sc-room-grid.cols-3 {
          grid-template-columns: repeat(2, 1fr);
        }
      }

      /* Rooms section label */
      .sc-rooms-label {
        font-size: var(--sc-font-sm);
        font-weight: 600;
        color: var(--sc-text-muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: var(--sc-space-sm);
        margin-top: var(--sc-space-md);
      }
    `],e([mt({attribute:!1})],t.SmartClimateCard.prototype,"hass",void 0),e([gt()],t.SmartClimateCard.prototype,"_config",void 0),e([gt()],t.SmartClimateCard.prototype,"_rooms",void 0),e([gt()],t.SmartClimateCard.prototype,"_detailRoom",void 0),e([gt()],t.SmartClimateCard.prototype,"_detailOpen",void 0),t.SmartClimateCard=e([ht("smart-climate-card")],t.SmartClimateCard),window.customCards=window.customCards||[],window.customCards.push({type:"smart-climate-card",name:"Smart Climate Card",description:"A comprehensive dashboard card for the Smart Climate HA integration. Shows room comfort, HVAC status, schedules, and AI suggestions.",preview:!0,documentationURL:"https://github.com/joshuaseidel/hass-climate-controll/tree/main/smart-climate-card"}),t}({});
