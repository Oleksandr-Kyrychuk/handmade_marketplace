import FooterBottom from "@/components/footer/FooterBottom";
import FooterTop from "@/components/footer/FooterTop";

function Footer() {
  return (
    <footer>
      <div className="container m-auto px-4">
        <FooterTop />
        <FooterBottom />
      </div>
    </footer>
  );
}

export default Footer;