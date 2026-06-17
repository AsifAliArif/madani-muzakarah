const Q_START = "\uFD3F";
const Q_END = "\uFD3E";

export function stripHtml(html: string): string {
  const div = document.createElement("div");
  div.innerHTML = html;
  return div.textContent || "";
}

export function buildShareText(title: string, contentHtml: string, authorName: string): string {
  const div = document.createElement("div");
  div.innerHTML = contentHtml;

  const processNode = (node: Node): string => {
    if (node.nodeType === Node.TEXT_NODE) return node.textContent || "";
    if (node.nodeType !== Node.ELEMENT_NODE) return "";
    const el = node as HTMLElement;
    const cls = el.className || "";
    let inner = Array.from(el.childNodes).map(processNode).join("");

    if (cls.includes("quran-text")) {
      if (!inner.startsWith(Q_START)) inner = `${Q_START}${inner}${Q_END}`;
      return `*${inner}*`;
    }
    if (cls.includes("arabic-text")) {
      return `*${inner}*`;
    }
    if (el.tagName === "STRONG" || el.tagName === "B") {
      return `*${inner}*`;
    }
    if (el.tagName === "P" || el.tagName === "DIV") {
      return inner + "\n";
    }
    return inner;
  };

  let body = Array.from(div.childNodes).map(processNode).join("").trim();
  const displayTitle = title || body.split("\n")[0] || "بلا عنوان";
  let text = `*${displayTitle}*\n\n${body}`;
  if (authorName.trim()) {
    text += `\n\n*تحریر از: ${authorName.trim()}*`;
  }
  return text;
}

export async function shareText(text: string, title: string) {
  if (navigator.share) {
    await navigator.share({ title, text });
  } else {
    await navigator.clipboard.writeText(text);
    alert("متن کاپی ہو گیا");
  }
}

export async function renderNoteElement(title: string, contentHtml: string, authorName: string): Promise<HTMLElement> {
  const container = document.createElement("div");
  container.dir = "rtl";
  container.style.cssText = "padding:32px;background:#fff;width:800px;font-family:'Mehr Nastaliq',serif;color:#212529;";

  const h = document.createElement("h1");
  h.style.cssText = "font-family:'Aslam',serif;font-size:28px;color:#084981;margin-bottom:24px;";
  h.textContent = title || "بلا عنوان";
  container.appendChild(h);

  const content = document.createElement("div");
  content.className = "note-content";
  content.style.fontSize = "21px";
  content.style.lineHeight = "1.9";
  content.innerHTML = contentHtml;
  container.appendChild(content);

  if (authorName.trim()) {
    const author = document.createElement("p");
    author.style.cssText = "margin-top:32px;font-size:18px;color:#084981;";
    author.textContent = `تحریر از: ${authorName.trim()}`;
    container.appendChild(author);
  }

  document.body.appendChild(container);
  return container;
}

export async function downloadAsImage(title: string, contentHtml: string, authorName: string) {
  const html2canvas = (await import("html2canvas")).default;
  const el = await renderNoteElement(title, contentHtml, authorName);
  const canvas = await html2canvas(el, { scale: 2, useCORS: true, backgroundColor: "#ffffff" });
  document.body.removeChild(el);
  const link = document.createElement("a");
  link.download = `${title || "note"}.png`;
  link.href = canvas.toDataURL("image/png");
  link.click();
}

export async function downloadAsPdf(title: string, contentHtml: string, authorName: string) {
  const { jsPDF } = await import("jspdf");
  const el = await renderNoteElement(title, contentHtml, authorName);
  const html2canvas = (await import("html2canvas")).default;
  const canvas = await html2canvas(el, { scale: 2, useCORS: true, backgroundColor: "#ffffff" });
  document.body.removeChild(el);

  const imgData = canvas.toDataURL("image/png");
  const pdf = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const imgWidth = pageWidth - 20;
  const imgHeight = (canvas.height * imgWidth) / canvas.width;

  let heightLeft = imgHeight;
  let position = 10;

  pdf.addImage(imgData, "PNG", 10, position, imgWidth, imgHeight);
  heightLeft -= pageHeight;

  while (heightLeft > 0) {
    position = heightLeft - imgHeight + 10;
    pdf.addPage();
    pdf.addImage(imgData, "PNG", 10, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;
  }

  pdf.save(`${title || "note"}.pdf`);
}

export async function shareAsFile(
  type: "image" | "pdf",
  title: string,
  contentHtml: string,
  authorName: string
) {
  const el = await renderNoteElement(title, contentHtml, authorName);
  const html2canvas = (await import("html2canvas")).default;
  const canvas = await html2canvas(el, { scale: 2, useCORS: true, backgroundColor: "#ffffff" });
  document.body.removeChild(el);

  if (type === "image") {
    const blob = await new Promise<Blob>((resolve) => canvas.toBlob((b) => resolve(b!), "image/png"));
    const file = new File([blob], `${title || "note"}.png`, { type: "image/png" });
    if (navigator.canShare?.({ files: [file] })) {
      await navigator.share({ files: [file], title });
    } else {
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = file.name;
      link.click();
    }
  } else {
    const { jsPDF } = await import("jspdf");
    const imgData = canvas.toDataURL("image/png");
    const pdf = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });
    const pageWidth = pdf.internal.pageSize.getWidth();
    const imgWidth = pageWidth - 20;
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    pdf.addImage(imgData, "PNG", 10, 10, imgWidth, imgHeight);
    const blob = pdf.output("blob");
    const file = new File([blob], `${title || "note"}.pdf`, { type: "application/pdf" });
    if (navigator.canShare?.({ files: [file] })) {
      await navigator.share({ files: [file], title });
    } else {
      pdf.save(file.name);
    }
  }
}
