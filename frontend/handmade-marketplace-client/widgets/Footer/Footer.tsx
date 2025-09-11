import {FooterTop, FooterBottom} from '.';

function Footer() {
  return (
    <footer className="bg-primary-900  pt-[80px] pb-4 text-snow">
      <div className="container m-auto px-4">
        <FooterTop />
        <FooterBottom />
      </div>
    </footer>
  );
}

export default Footer;