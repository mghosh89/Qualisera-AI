"""Parse pytest JUnit XML -> HTML dashboard with totals + scenario rows."""
import xml.etree.ElementTree as ET


def render(xml_path, out_path="dashboard.html"):
    root = ET.parse(xml_path).getroot()
    tests = int(root.get("tests", 0)); fails = int(root.get("failures", 0))
    rows = "".join(
        f"<tr><td>{tc.get('classname')}</td><td>{tc.get('name')}</td>"
        f"<td>{'PASS' if len(tc.findall('failure'))==0 else 'FAIL'}</td></tr>"
        for tc in root.iter("testcase"))
    html = (f"<html><body><h2>QualiseraAI — {tests} tests, {fails} failures"
            f"</h2><table border=1>{rows}</table></body></html>")
    open(out_path, "w").write(html)
    return out_path