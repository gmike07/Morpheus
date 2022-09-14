#include "cc_logging_objects.hh"
#include "cc_logging.hh"
#include "cc_socket_helper.hh"
#include <string>

const int MILLISECONDS_TO_SLEEP = 1;


void create_handlers(SocketHelper& socket_helper, std::vector<std::unique_ptr<DefaultHandler>>& handlers, ServerSender& sender)
{
  if(socket_helper.scoring_path != "")
  {
    handlers.push_back(std::unique_ptr<DefaultHandler>(new ScoreHandler(socket_helper)));
  }
  if(socket_helper.server_path != "")
  {
    handlers.push_back(std::unique_ptr<DefaultHandler>(new StateServerHandler(socket_helper, std::make_shared<ChunkHistory>(socket_helper), sender)));
  }
}


/*
 * handles the thread to store statistics of the socket and change the cc
*/
void logging_cc_func(TCPSocket* socket)
{
  if(socket == nullptr)
  {
    std::cout << "oh shit, socket doesn't exists" << std::endl;
    return;
  }
  while(!socket->created_socket) {}
  TCPSocket& sock = *socket;
  SocketHelper* sock_helper = sock.socket_helper_p.get();
  std::vector<std::unique_ptr<DefaultHandler>> handlers(0);
  std::shared_ptr<ServerSender> sender(new ServerSender(*sock_helper, sock_helper->server_path));
  create_handlers(*sock_helper, handlers, *sender);
  std::this_thread::sleep_for(std::chrono::milliseconds(MILLISECONDS_TO_SLEEP));

  try{
    while(sock_helper->connection_id() == 0)
    {
      for(auto& handler: handlers)
      {
        (*handler.get())();
      }
      std::this_thread::sleep_for(std::chrono::milliseconds(MILLISECONDS_TO_SLEEP));
    }
  }
  catch (const std::exception& e)
  {
      sender->send_and_receive_str("sock finished");
      std::cerr << e.what() << "hmmm" << std::endl;
  }
  catch (...)
  {
      sender->send_and_receive_str("sock finished");
      std::cerr << "hmmm error 2" << std::endl;
  }
}
