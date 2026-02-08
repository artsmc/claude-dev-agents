/**
 * Test fixture: JavaScript XSS vulnerabilities.
 *
 * THIS FILE CONTAINS INTENTIONALLY VULNERABLE CODE FOR TESTING PURPOSES.
 * All code patterns are designed to validate the InjectionAnalyzer's
 * JavaScript XSS and code injection detection capabilities.
 *
 * Expected detections by InjectionAnalyzer:
 *   - xss-vulnerability (HIGH, line ~18) - innerHTML assignment
 *   - xss-vulnerability (HIGH, line ~23) - dangerouslySetInnerHTML
 *   - xss-vulnerability (HIGH, line ~30) - document.write
 *   - code-injection (HIGH, line ~35) - eval usage
 *   - xss-vulnerability (HIGH, line ~40) - outerHTML assignment
 *
 * Total expected findings: 5
 */

// VULN: XSS via innerHTML assignment
function renderUserComment(comment) {
  document.getElementById("output").innerHTML = comment;
}

// VULN: XSS via dangerouslySetInnerHTML in React component
function UnsafeComponent({ userHtml }) {
  return React.createElement("div", {
    dangerouslySetInnerHTML: { __html: userHtml }
  });
}

// VULN: XSS via document.write
function writeContent(content) {
  document.write(content);
}

// VULN: Code injection via eval
function processExpression(expr) {
  return eval(expr);
}

// VULN: XSS via outerHTML assignment
function replaceElement(element, html) {
  element.outerHTML = html;
}

// Safe: Using textContent (not vulnerable to XSS)
function safeRender(text) {
  document.getElementById("output").textContent = text;
}

// Safe: Using DOMPurify sanitization
function safeInnerHtml(html) {
  document.getElementById("output").innerHTML = DOMPurify.sanitize(html);
}
